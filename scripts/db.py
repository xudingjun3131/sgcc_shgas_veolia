"""数据库抽象层：统一 SQLite / MySQL 接口，子类只负责连接和 SQL 执行。

表结构（两种数据库一致，EAV 模式）：
- daily{user_id}: date(PRIMARY KEY), usage(REAL)           -- 每日用电量
- data{user_id}:  name(PRIMARY KEY), value(TEXT)            -- 扩展数据（月度/年度/用户信息等）
"""

import logging
import os

# ── SQLite ──
import sqlite3

# ── MySQL ──（可选，仅 DB_TYPE=mysql 时导入）
try:
    import mysql.connector
    _HAS_MYSQL = True
except ImportError:
    _HAS_MYSQL = False


class DB:
    """数据库基类：定义统一数据操作接口。子类只需实现连接/执行/关闭/建表。"""

    # ── 子类需覆写的方言属性 ──
    db_type: str = "base"

    # ── 子类需实现的方法 ──

    def _connect(self):
        raise NotImplementedError

    def _execute(self, sql: str):
        """执行一条写 SQL 并 commit。"""
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError

    def _create_tables(self, user_id: str) -> bool:
        raise NotImplementedError

    # ── 统一接口 ──

    def connect_user_db(self, user_id: str) -> bool:
        try:
            self._connect()
            self.table_name = f"daily{user_id}"
            self.table_expand_name = f"data{user_id}"
            return self._create_tables(user_id)
        except Exception as e:
            logging.error(f"[{self.db_type}] 连接/建表失败: {e}")
            return False

    def close_connect(self):
        try:
            self._close()
        except Exception:
            pass

    # ── 数据写入方法（子类共用，无需覆写） ──

    def upsert_user(self, user_id: str, username: str, user_name: str):
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_expand_name} VALUES"
            f"('user_info', '{user_id}|{username}|{user_name}')")

    def insert_balance_log(self, data: dict):
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_expand_name} VALUES"
            f"('balance_{data.get('date', 'latest')}', "
            f"'{data.get('balance', 0)}|{data.get('user_name', '')}|"
            f"{data.get('as_of', '')}|{data.get('amount_due', '')}')")

    def insert_daily_data(self, data: dict):
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_name} VALUES"
            f"('{data['date']}', {data['total_usage']})")

    def insert_monthly_data(self, data: dict):
        month_key = data.get('month') or data.get('date', '')
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_expand_name} VALUES"
            f"('month_{month_key}', "
            f"'{data.get('total_usage', 0)}|{data.get('total_charge', 0)}|"
            f"{data.get('valley_usage', '')}|{data.get('flat_usage', '')}|"
            f"{data.get('peak_usage', '')}|{data.get('tip_usage', '')}|"
            f"{data.get('user_name', '')}')")

    def insert_yearly_data(self, data: dict):
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_expand_name} VALUES"
            f"('year_{data.get('year', '')}', "
            f"'{data.get('total_usage', 0)}|{data.get('total_charge', 0)}|"
            f"{data.get('user_name', '')}')")

    def insert_data(self, data: dict):
        """原始每日数据写入（兼容旧调用）"""
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_name} VALUES"
            f"('{data['date']}', {data['usage']})")

    def insert_expand_data(self, data: dict):
        """原始扩展数据写入（兼容旧调用）"""
        self._execute(
            f"INSERT OR REPLACE INTO {self.table_expand_name} VALUES"
            f"('{data['name']}', '{data['value']}')")

    def cleanup_old_data(self):
        try:
            days = int(os.getenv("DATA_RETENTION_DAYS", 365))
            self._execute(
                f"DELETE FROM {self.table_name} "
                f"WHERE date < date('now', '-{days} days')")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# SQLite 实现
# ═══════════════════════════════════════════════════════════

class SqliteDB(DB):
    db_type = "sqlite"

    def _connect(self):
        db_name = os.getenv("DB_NAME", "homeassistant.db")
        if "PYTHON_IN_DOCKER" in os.environ:
            db_name = "/data/" + db_name
        self._conn = sqlite3.connect(db_name)
        logging.info(f"[sqlite] 已连接 {db_name}")

    def _execute(self, sql: str):
        self._conn.execute(sql)
        self._conn.commit()

    def _close(self):
        if getattr(self, "_conn", None):
            self._conn.close()
            self._conn = None
            logging.info("[sqlite] 已关闭")

    def _create_tables(self, user_id: str) -> bool:
        self._conn.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            date DATE PRIMARY KEY NOT NULL,
            usage REAL NOT NULL)""")
        logging.info(f"[sqlite] 表 {self.table_name} OK")
        self._conn.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_expand_name} (
            name TEXT PRIMARY KEY NOT NULL,
            value TEXT NOT NULL)""")
        self._conn.commit()
        logging.info(f"[sqlite] 表 {self.table_expand_name} OK")
        return True


# ═══════════════════════════════════════════════════════════
# MySQL 实现
# ═══════════════════════════════════════════════════════════

class MysqlDB(DB):
    db_type = "mysql"

    def _connect(self):
        if not _HAS_MYSQL:
            raise RuntimeError("mysql-connector-python 未安装")
        self._conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
        )
        if self._conn.is_connected():
            logging.info(f"[mysql] 已连接 {os.getenv('MYSQL_DATABASE')}")
        else:
            raise ConnectionError("MySQL 连接失败")

    def _execute(self, sql: str):
        # REPLACE INTO 语法替换
        sql = sql.replace("INSERT OR REPLACE INTO", "REPLACE INTO")
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
            self._conn.commit()
        finally:
            cursor.close()

    def _close(self):
        if getattr(self, "_conn", None) and self._conn.is_connected():
            self._conn.close()
            self._conn = None
            logging.info("[mysql] 已关闭")

    def _create_tables(self, user_id: str) -> bool:
        self._execute(f"""CREATE TABLE IF NOT EXISTS `{self.table_name}` (
            `date` DATE PRIMARY KEY NOT NULL,
            `usage` REAL NOT NULL)""")
        logging.info(f"[mysql] 表 {self.table_name} OK")
        self._execute(f"""CREATE TABLE IF NOT EXISTS `{self.table_expand_name}` (
            `name` varchar(100) PRIMARY KEY NOT NULL,
            `value` TEXT NOT NULL)""")
        logging.info(f"[mysql] 表 {self.table_expand_name} OK")
        return True


# ═══════════════════════════════════════════════════════════
# 工厂函数
# ═══════════════════════════════════════════════════════════

def create_db(db_type: str) -> DB:
    """根据配置创建数据库实例。"""
    t = db_type.lower()
    if t == "mysql":
        return MysqlDB()
    return SqliteDB()
