import pickle


with open('model.pickle', 'rb') as handle:
	model = pickle.load(handle)


pred = model.predict(["Sterling completed a season-long loan move to the Emirates Stadium from Chelsea on the deadline day after he was deemed surplus to Blues boss Enzo Maresca's needs. After officially putting pen to paper on a Gunners deal, he watched his new club in action against Brighton on Saturday. On Tuesday, he was handed over his new shirt number, 30. Sterling was elated to join a club like Arsenal, who in the last two seasons had handed champions Manchester City a run for their money in the Premier League title race. The England international believes Mikel Arteta's side are a 'perfect fit' for him as they complement his hunger for success. In his first exclusive interview with the club's official website, the 29-year-old said, I’m buzzing. It’s one where we left it late but it’s one I was hoping for. Looking at everything, I’m just like: ‘this is a perfect fit for me’, and I’m super happy that we got it over the line. It’s a perfect fit for me to be at a football club like this, where you can see that hunger, that desire, year on year, they are pushing and pushing and pushing. That’s exactly how I am as a person.Each year you want to get better and do better than the previous year. Hopefully, I can gel really well with the boys and get going. It’s time now to meet the boys, get settled in and hopefully now see some game time and make my mark."])
result = format(pred[0])

print(result)