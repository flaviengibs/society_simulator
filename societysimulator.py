import random
import time
import json
import os
import math

class Society:
    def __init__(self):
        self.day = 1
        self.population = 100
        self.happiness = 70.0
        self.money = 30000.0
        self.tax_rate = 15
        self.services = {
            "santé": 0,
            "loisirs": 0,
            "sécurité": 0,
        }
        self.projects = []
        self.resources = {"eau": 250, "énergie": 250}
        self.usines_count = 0
        self.station_d_epuration_count = 0
        self.temp_happiness_bonus = 0
        self.last_tax_rate = self.tax_rate

    def apply_daily_changes(self):
        income = self.population * (self.tax_rate / 100) * 250
        self.money += income
        daily_cost = sum(self.services.values())
        self.money -= daily_cost
        self.resources["eau"] -= math.ceil(self.population / 2)
        self.resources["énergie"] -= math.ceil(self.population / 2)

        if self.temp_happiness_bonus:
            self.happiness += self.temp_happiness_bonus

        if self.tax_rate > 15:
            self.happiness -= 0.3 * (self.tax_rate - 15)

        if self.happiness > 75:
            growth = int((self.happiness - 70) / 5)
            self.population += random.randint(2, 5 + growth)
        elif self.happiness < 50:
            loss = int((50 - self.happiness) / 5)
            self.population -= random.randint(2, 5 + loss)

        if self.usines_count >= 1 or self.station_d_epuration_count >= 1:
            if self.usines_count >= 1:
                self.resources["énergie"] += self.usines_count * 10 
            else:
                self.resources["eau"] += self.station_d_epuration_count * 10 

        if self.resources["eau"] <= 0 or self.resources["énergie"] <= 0:
            print("Pénurie de ressources !")
            self.happiness -= 5

        self.population = max(10, self.population)
        self.happiness = max(0, min(100, self.happiness))
        self.trigger_random_event()

        if self.day % 7 == 0:
            self.weekly_report()
        self.day += 1

    def show_stats(self):
        print(f"\n Jour {self.day}")
        print(f" Population : {self.population}")
        print(f" Bonheur    : {self.happiness:.1f}")
        print(f" Argent     : {self.money:.2f} €")
        print(f" Impôts     : {self.tax_rate}%")
        print(f" Eau        : {self.resources['eau']}")
        print(f" Énergie    : {self.resources['énergie']}")
        print("️  Dépenses (quotidiennes) :")
        for k, v in self.services.items():
            print(f"   - {k.capitalize()} : {v} € / jour")
        if self.projects:
            print("️  Projets : ", ", ".join(self.projects))

    def next_day(self):
        self.apply_daily_changes()

    def set_tax_rate(self):
        try:
            new_tax = int(input(" Nouveau taux d'imposition (0-50%) : "))
            if 0 <= new_tax <= 50:
                if new_tax < self.tax_rate:
                    bonus = 0.5 * (self.tax_rate - new_tax)
                    self.temp_happiness_bonus += bonus
                    print(f" Baisse d'impôts (+{bonus:.1f} bonheur)")
                self.last_tax_rate = self.tax_rate
                self.tax_rate = new_tax
            else:
                print(" Taux invalide.")
        except ValueError:
            print(" Entrée non valide.")

    def manage_services(self):
        print("\n Services publics.")
        total_spend = 0
        for service in self.services:
            try:
                val = int(input(f"   {service.capitalize()} (actuel : {self.services[service]}) : "))
                if val >= 0:
                    total_spend += val - self.services[service]
                    self.services[service] = val
            except ValueError:
                print(" Non valide.")
        if total_spend > 0:
            bonus = total_spend / 3333
            self.temp_happiness_bonus += bonus
            print(f" Investissement (+{bonus:.1f} bonheur)")

    def build_project(self):
        print("\n Construire un projet :")
        projets = {
            "Parc": {"coût": 5000, "bonheur": 7},
            "École": {"coût": 10000, "bonheur": 10},
            "Usine": {"coût": 12000, "énergie": 50},
            "Station d'épuration": {"coût": 12000, "eau": 50}
        }
        for i, p in enumerate(projets):
            print(f"{i+1}. {p} ({projets[p]})")
        choix = input("Choix : ")
        try:
            choix = int(choix)
            nom = list(projets)[choix-1]
            data = projets[nom]
            if self.money >= data.get("coût", 0):
                self.money -= data.get("coût", 0)
                self.projects.append(nom)
                self.temp_happiness_bonus += data.get("bonheur", 0)
                self.resources["énergie"] += data.get("énergie", 0)
                self.resources["eau"] += data.get("énergie", 0)
                if nom == "Usine":
                    self.usines_count += 1
                elif nom == "Station d'épuration":
                    self.station_d_epuration_count += 1
                print(f" {nom} construit.")
            else:
                print(" Pas assez d'argent.")
        except:
            print(" Erreur.")

    def trigger_random_event(self):
        events = [
            {"chance": 0.08, "text": " Une fête locale (+5 Bonheur)", "effect": lambda: self._adjust_happiness(5)},
            {"chance": 0.1, "text": " Épidémie (-10 hab)", "effect": lambda: self._adjust_population(-10)},
            {"chance": 0.07, "text": " Incendie (-3000€)", "effect": lambda: self._adjust_money(-3000)},
            {"chance": 0.05, "text": " Don de mécène (+5000€)", "effect": lambda: self._adjust_money(5000)},
            {"chance": 0.1, "text": " Don de ressources (+50 énergie, +50 eau)", "effect": lambda: self._adjust_resources(50)},
        ]
        for event in events:
            if random.random() < event["chance"]:
                print(f"\n {event['text']}")
                event["effect"]()

    def _adjust_happiness(self, delta):
        self.happiness = max(0, min(100, self.happiness + delta))

    def _adjust_population(self, delta):
        self.population = max(10, self.population + delta)

    def _adjust_money(self, delta):
        self.money = max(0, self.money + delta)

    def _adjust_resources(self, delta):
        self.resources["eau"] = max(0, self.resources["eau"] + delta)
        self.resources["énergie"] = max(0, self.resources["énergie"] + delta)

    def weekly_report(self):
        print("\n Rapport Hebdomadaire")
        print("+----------------------------+")
        print(f"| Population : {self.population:<10}     |")
        print(f"| Bonheur    : {self.happiness:<10.1f}     |")
        print(f"| Argent     : {self.money:<10.2f} € |")
        print("+----------------------------+")

    def save(self):
        with open("save.json", "w") as f:
            json.dump(self.__dict__, f)
        print(" Sauvegarde effectuée.")

    def load(self):
        if os.path.exists("save.json"):
            with open("save.json", "r") as f:
                data = json.load(f)
                self.__dict__.update(data)
            print(" Sauvegarde chargée.")
        else:
            print(" Aucune sauvegarde trouvée.")

def main():
    society = Society()
    if input("Charger une sauvegarde ? (o/n) : ").lower() == "o":
        society.load()
    print(" Simulateur de société")
    while True:
        society.show_stats()
        print("\nActions :")
        print("1. Jour suivant")
        print("2. Modifier impôts")
        print("3. Gérer services")
        print("4. Construire projet")
        print("5. Sauvegarder")
        print("6. Quitter")
        choix = input("Choix : ")
        if choix == "1":
            society.next_day()
        elif choix == "2":
            society.set_tax_rate()
        elif choix == "3":
            society.manage_services()
        elif choix == "4":
            society.build_project()
        elif choix == "5":
            society.save()
        elif choix == "6":
            break
        time.sleep(0.6)

if __name__ == "__main__":
    main()
