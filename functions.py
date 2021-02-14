def is_worker(user):
    """ Function to check the user type: Dog_Owner or Dog_Walker """
    try:
        user.description

    except AttributeError:
        return False
    
    return True

def calculate_dog_walker_rate(db, dog_walker):
    """ Function that will get the rate average for an specific dog_walker """

    appointments = dog_walker.appointments

    reviews_list = [aptment.review for aptment in appointments if len(aptment.review) > 0]
    rates = []

    for reviews in reviews_list:
        for review in reviews:
            rates.append(review.rate)

    average = sum(rates)/len(rates)

    dog_walker.rate = average
    db.session.add(dog_walker)
    db.session.commit()







