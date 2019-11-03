from app import db, User,Picture

if __name__ == '__main__':
    id = 1
    pictures = Picture.query.all()
    images = []
    for pic in pictures:
        if pic.picture_caption.lower().find('ZARA'.lower()) != -1 and not pic.is_private:
            images.append({"image_id": pic.pid, "Caption": pic.picture_caption, "link": pic.picture_link})
    print(images)

    # db.drop_all()
    # db.create_all()
    # # user1 = User('umarfaruk.chwodhury@gmail.com','opensesame','Umar')
    # # db.session.add(user1)
    # # db.session.commit()
    # pictures = db.session.query(Picture.picture_link,User.name).filter(Picture.is_private==0).filter(User.uid == Picture.owner_id).all()
    #
    #
    # print(pictures)
    # print("Outside")
    # for picture in pictures:
    #     print("inside")
    #     print('Name: {} Picture Link {}'.format(picture.name,picture.picture_link))
