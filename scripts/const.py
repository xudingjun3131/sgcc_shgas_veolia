# 填写普通参数 不要填写密码等敏感信息
# 国网电力官网
LOGIN_URL = "https://www.95598.cn/osgweb/login"
ELECTRIC_USAGE_URL = "https://www.95598.cn/osgweb/electricityCharge"
BALANCE_URL = "https://www.95598.cn/osgweb/userAcc"


# Home Assistant
SUPERVISOR_URL = "http://supervisor/core"
API_PATH = "/api/states/" # https://developers.home-assistant.io/docs/api/rest/

BALANCE_SENSOR_NAME = "sensor.electricity_charge_balance"
DAILY_USAGE_SENSOR_NAME = "sensor.last_electricity_usage"
YEARLY_USAGE_SENSOR_NAME = "sensor.yearly_electricity_usage"
YEARLY_CHARGE_SENSOR_NAME = "sensor.yearly_electricity_charge"
MONTH_USAGE_SENSOR_NAME = "sensor.month_electricity_usage"
MONTH_CHARGE_SENSOR_NAME = "sensor.month_electricity_charge"
BALANCE_UNIT = "CNY"
USAGE_UNIT = "KWH"
USAGE_UNIT_CUBE = "m³"

# 上海燃气实体定义
SHRQ_BALANCE_SENSOR_NAME = "sensor.shrq_charge_balance"   # 本期消费
SHRQ_MONTHLY_USAGE_SENSOR_NAME = "sensor.last_shrq_usage"   # 本期用量 字
SHRQ_YEARLY_USAGE_SENSOR_NAME = "sensor.yearly_shrq_usage"  # 燃气年用量 字


# 浦东威立雅水费实体定义
PDWLY_MONTHLY_USAGE_TOTAL_SENSOR_NAME = "sensor.last_pdwly_usage_total"   # 本期消费 m³
PDWLY_MONTHLY_USAGE_WATER_SENSOR_NAME = "sensor.last_pdwly_usage_water"   # 本期消费 生活水m³
PDWLY_MONTHLY_USAGE_DIRTY_SENSOR_NAME = "sensor.last_pdwly_usage_dirty"   # 本期消费 污水m³
PDWLY_MONTHLY_CHARGE_TOTAL_SENSOR_NAME = "sensor.last_pdwly_charge_total"   # 本期消费
PDWLY_MONTHLY_CHARGE_WATER_SENSOR_NAME = "sensor.last_pdwly_charge_water"   # 本期消费 生活水
PDWLY_MONTHLY_CHARGE_DIRTY_SENSOR_NAME = "sensor.last_pdwly_charge_dirty"   # 本期消费 污水
