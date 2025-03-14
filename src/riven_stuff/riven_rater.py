"""Class used to calculate the best grades for each riven,
the punctuation system is based off pricings on different
platforms and trade chat.
It uses the weapon, its type, class, uses, stats...
"""
import src.settings as settings
import src.utils as utils


class Profile:
    """Class used to calculate the best grades for each riven,
    the punctuation system is based off pricings on different
    platforms and trade chat.
    It uses the weapon, its type, class, uses, stats...
    """

    def __init__(self, name, weapon_type, stat_weights, equations):
        self.name = name
        self.weapon_type = weapon_type
        self.stat_weights = stat_weights
        self.equations = equations

    def evaluate_stats(self, riven):
        """The method searches for the weight of the stats based on the
        weapon class, type and stats and its equation, then calculates
        a total rating for the riven"""

        punctuation = 0
        worst = 99
        for stat, grade in zip(riven.stats, riven.grades):
            weight = self.stat_weights[stat[1]][not stat[0]]
            equation = eval(self.equations[stat[1]])
            if equation < worst and stat[0]:
                worst = equation
            punctuation += equation
            if -10 < grade < 11:
                punctuation += (
                    weight * grade * 0.02 if stat[0] else weight * -grade * 0.02
                )
        if worst < 5:
            return punctuation - 20

        return punctuation


def generate_profiles():
    """Method used to load the profiles that'll be used"""

    for i, w_type in enumerate(settings.weights):
        for key, val in w_type.items():
            settings.profiles.append(Profile(key, i, val, settings.equations[i][key]))


def find_profiles(riven):
    """Method used to find the profiles that'll be used for the weapon, should rework it"""

    profiles = []
    for prof in settings.profiles:
        if prof.weapon_type == riven.riven_type:
            profiles.append(prof)
    return profiles


def profile_management(riven, prof, punct):
    """Method used to filter the profiles punctuation"""
    if prof.name == "Beam" and riven.weapon["attack_name"] not in ["Beam", "Held"]:
        punct = 0
    elif (
        prof.name == "Eidolon hunting - Vectis"
        and "vectis" not in riven.weapon_name.lower()
        or prof.name == "Eidolon hunting - Rubico"
        and "rubico" not in riven.weapon_name.lower()
    ):
        punct = 0
    elif riven.riven_type == 3:
        if prof.name == "Heavy" and (
            riven.weapon["class"]
            not in [
                "Gunblade",
                "Scythe",
                "Two-handed nikana",
                "Dual daggers",
                "Dagger",
                "Rapier",
                "Claws",
                "Hammer",
                "Machete",
            ]
            and riven.weapon_name not in ["paracesis", "korrudo"]
        ):
            punct /= 1.75
        if prof.name == "Glaive" and riven.weapon["class"] != "Glaive":
            punct = 0
        if prof.name != "Glaive" and riven.weapon["class"] == "Glaive":
            punct = 0
        if prof.name != "Gunblade" and "Gunblade" in riven.weapon["class"]:
            punct = 0
        if prof.name == "Gunblade" and "Gunblade" not in riven.weapon["class"]:
            punct = -20
        if riven.disposition[0] < 1.1 and "statstick" in prof.name:
            punct = punct * riven.disposition[0] / 2
    if (
        riven.riven_type == 2
        and prof.name == "Co-primer"
        and riven.weapon_name not in ["epitaph", "nukor", "cycron"]
    ):
        punct = -20
    if ("Rubico" in prof.name and "rubico" not in riven.weapon_name) or (
        "Vectis" in prof.name and "vectis" not in riven.weapon_name
    ):
        punct = -20
    elif (
        "rubico" in riven.weapon_name or "vectis" in riven.weapon_name
    ) and prof.name == "General use":
        punct /= 2

    return punct


def rate_riven(riven):
    """Searches for the weapon profiles, then executes them and chooses
    the best out of them, returning the best riven punctuation"""
    profiles = find_profiles(riven)
    initial_punct = -30
    if not riven.stats[-1][0]:
        initial_punct += 20
        a, b = 15, 0
        if len(riven.stats) == 3:
            a, b = b, a
        initial_punct += utils.scale_range(riven.disposition[0], 0.5, 1.5, a, b)

    punct_list = []
    for prof in profiles:
        punct_list.append(
            [
                prof.name,
                round(
                    utils.scale_range(
                        profile_management(
                            riven, prof, initial_punct + prof.evaluate_stats(riven)
                        ),
                        -30,
                        95,
                        0,
                        100,
                    ),
                    2,
                ),
            ]
        )

    if len(punct_list) == 0:
        print("xd")
    return sorted(punct_list, key=lambda punct: punct[1], reverse=True)
