# 导入所有模型，以便Alembic可以自动检测到它们
from app.db.base_class import Base
from app.models.user import User
# 在这里导入其他模型
# from app.models.keyword import Keyword
# from app.models.news import News
# 等等 