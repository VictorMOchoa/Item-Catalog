from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Item, Category

engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Delete any existing data before creating the new objects below
session.query(User).delete()
session.query(Item).delete()
session.query(Category).delete()

# Create a first user (myself)
firtUser = User(name="Victor Ochoa",
                email="victor.ochoa@csu.fullerton.edu",
                picture="http://img.sharetv.com/shows/characters/large/"
                "happy_days.richard_richie_cunningham.jpg")
session.add(firtUser)
session.commit()

# Create a few initial categories
mma = Category(name="Mixed Martial Arts",
               user_id=1)
session.add(mma)
session.commit()

football = Category(name="Football",
                    user_id=1)
session.add(football)
session.commit()

baseball = Category(name="Baseball",
                    user_id=1)
session.add(baseball)
session.commit()

basketball = Category(name="Basketball",
                      user_id=1)
session.add(basketball)
session.commit()

soccer = Category(name="Soccer",
                  user_id=1)
session.add(soccer)
session.commit()

# Create a few initial items for one of the categories
gloves = Item(name="Fight Gloves",
              description="4oz gloves to wear for fighting",
              picture="https://i5.walmartimages.com/asr/2d139f50-8352-4322"
              "-8872-ee0f2f1b2738_1.59af6518e77215b3641973eeda2273cc.jpeg",
              category_id=1,
              user_id=1)
session.add(gloves)
session.commit()

mouthpiece = Item(name="Mouthpiece",
                  description="Rubber and moldable mouthpiece to protect your"
                  "mouth during combat",
                  picture="https://www.fullcontactway.com/wp-content/"
                  "uploads/2017/02/Venum-3.jpg",
                  category_id=1,
                  user_id=1)
session.add(mouthpiece)
session.commit()

handwraps = Item(name="Hand Wraps",
                 description="Designed to protect against common injuries"
                 "of the hands and wrists",
                 picture="https://i.ebayimg.com/images/g/D5AAAOxyB9RS1BTq/"
                 "s-l300.jpg",
                 category_id=1,
                 user_id=1)
session.add(handwraps)
session.commit()

football_helmet = Item(name="Steelers helmet",
                       description="Designed to protect your head",
                       picture="https://images.footballfanatics.com/FFImage/"
                       "thumb.aspx?i=/productimages/_2517000/"
                       "ff_2517594_full.jpg",
                       category_id=2,
                       user_id=1)
session.add(football_helmet)
session.commit()

basketball_shorts = Item(name="Basketball Shorts",
                         description="Breathable, moisture-wicking material",
                         picture="https://images.sportsdirect.com/images/"
                         "products/63796940_l.jpg",
                         category_id=4,
                         user_id=1)
session.add(basketball_shorts)
session.commit()

baseball_bat = Item(name="Baseball Bat",
                    description="Lightweight with plenty of punch",
                    picture="https://images-na.ssl-images-amazon.com/images/I"
                    "/51isBDNfbbL._SL1000_.jpg",
                    category_id=3,
                    user_id=1)
session.add(baseball_bat)
session.commit()
