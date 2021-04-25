from src.jsonlink import JsonLink


class Car(JsonLink):
    def __init__(self, color="", model=""):
        self.color = color
        self.model = model
        self.hidden_value = ""
        super(Car, self).__init__(use_keywords_file=True)

    def cool_func(self, passed_in):
        self.hidden_value = passed_in
        print("Hey that's pretty neat")

    def __repr__(self):
        return f"""
        Color  : {self.color}
        Model  : {self.model}
        Hidden : {self.hidden_value}
        """


blue_guyferrari = Car(color="", model="")
blue_guyferrari.update_from_dict(
    {"color": "green", "model": "Corola", "cool_func": "not new data"}
)

print(blue_guyferrari.get_default_state(save_to_file=True))
