from app import db, User,Picture

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    # user1 = User('umarfaruk.chwodhury@gmail.com','opensesame','Umar')
    # db.session.add(user1)
    # db.session.commit()
    pictures = db.session.query(Picture.picture_link,User.name).filter(Picture.is_private==0).filter(User.uid == Picture.owner_id).all()


    print(pictures)
    print("Outside")
    for picture in pictures:
        print("inside")
        print('Name: {} Picture Link {}'.format(picture.name,picture.picture_link))