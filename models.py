from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from database import Base
import enum


class StartAppEnum(enum.Enum):
    NEWS = "NEWS"
    RADIOS = "RADIOS"


class RoleEnum(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    GUEST = "GUEST"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    avatar = Column(String,
                    default="https://ik.imagekit.io/7whoa8vo6/lepiant/avatars/a388a057fd087204dd4b5cd90b79f54c"
                            "-sticker%201__Npxb9iIU.png")
    language = Column(String, default="fr")
    country = Column(String, default="sn")
    isActive = Column(Boolean, default=True)
    allowNotifications = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')
    defaultStartedPage = Column(Enum(StartAppEnum), default=StartAppEnum.NEWS)
    defaultArticleCategorie = Column(Integer, default=1)
    password = Column(String)


class ArticleCategorie(Base):
    __tablename__ = 'article_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    logo = Column(String, nullable=False)
    fullLogo = Column(String, nullable=False)
    country = Column(String, nullable=False)
    language = Column(String, default="fr")
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')
    webSite = Column(String, nullable=False)


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    categorieId = Column(Integer, ForeignKey('article_categories.id'))
    channelId = Column(Integer, ForeignKey('channels.id'))
    title = Column(String, unique=True, index=True)
    image = Column(String, default="https://ik.imagekit.io/7whoa8vo6/lepiant/a6a6a6_text=L_27EPIANT_LxvtvPYyB")
    description = Column(String, nullable=False)
    link = Column(String, unique=True, index=True)
    isActive = Column(Boolean, default=True)
    published = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')


class ArticleSaved(Base):
    __tablename__ = 'articles_saved'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'))
    articleId = Column(Integer, ForeignKey('articles.id'))


class ChannelSubscribed(Base):
    __tablename__ = 'channels_subscribed'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'))
    channelId = Column(Integer, ForeignKey('channels.id'))


class RadioCategorie(Base):
    __tablename__ = 'radio_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')


class Radio(Base):
    __tablename__ = 'radios'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    source = Column(String, nullable=False)
    image = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    categorieId = Column(Integer, ForeignKey('radio_categories.id'))


class RadioLiked(Base):
    __tablename__ = 'radios_liked'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'))
    radioId = Column(Integer, ForeignKey('radios.id'))


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, index=True)
    categorieId = Column(Integer, ForeignKey('article_categories.id'))
    channelId = Column(Integer, ForeignKey('channels.id'))
    url = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, default='now()')
    updatedAt = Column(DateTime, default='now()', onupdate='now()')
    language = Column(String, default="fr")


class Quotidien(Base):
    __tablename__ = 'quotidiens'

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default='now()')
    images = Column(String, unique=True, nullable=False)
    publishedAt = Column(String, nullable=False)
    thumbnailUrl = Column(String, default="")


class Revue(Base):
    __tablename__ = 'revues'

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default='now()')
    audio = Column(String, nullable=False)
    name = Column(String, unique=True, index=True)
    publishedAt = Column(String, nullable=False)


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'))
    sessionKey = Column(String, unique=True, index=True)
    sessionData = Column(String, nullable=False)
    userAgent = Column(String, nullable=False)
    lastActivity = Column(DateTime, nullable=False)
    createAt = Column(DateTime, nullable=False)
    expireAt = Column(DateTime, nullable=False)

