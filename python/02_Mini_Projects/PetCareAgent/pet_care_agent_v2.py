import random

# ---------------------------------------------------------------------------
# Schedule data
# ---------------------------------------------------------------------------

BUSINESS_HOURS = {
    "Monday": "9:00 AM - 6:00 PM",
    "Tuesday": "9:00 AM - 6:00 PM",
    "Wednesday": "9:00 AM - 6:00 PM",
    "Thursday": "9:00 AM - 6:00 PM",
    "Friday": "9:00 AM - 6:00 PM",
    "Saturday": "10:00 AM - 4:00 PM",
    "Sunday": "Closed",
}

# Checkup slots only ever land on the hour or half hour, during business
# hours, so a random pick still reads like a real clinic schedule instead
# of an arbitrary timestamp like "3:47 AM".
CHECKUP_SLOT_POOL = [
    "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
    "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM",
    "4:00 PM", "4:30 PM", "5:00 PM",
]

# Walk-ins only ever open up in one of these fixed windows.
WALK_IN_WINDOWS = [
    "8:00 AM - 9:00 AM",
    "12:00 PM - 1:00 PM",
    "5:00 PM - 6:00 PM",
]


def get_available_checkup_slots(count=4):
    """Randomly pick a handful of open slots from the fixed daily schedule."""
    count = min(count, len(CHECKUP_SLOT_POOL))
    picks = random.sample(CHECKUP_SLOT_POOL, count)
    return sorted(picks, key=CHECKUP_SLOT_POOL.index)


def is_walk_in_available():
    """About 2 out of 3 days, walk-ins happen to be open."""
    return random.random() < 0.66


# ---------------------------------------------------------------------------
# "Other" information menu
# ---------------------------------------------------------------------------

def other_info():
    while True:
        print("\n--- Other Information ---")
        print("What would you like to know?")
        print('  Type "timings"  - hear our business hours')
        print('  Type "walkins"  - check today\'s walk-in availability')
        print('  Type "checkup"  - see open pet checkup appointment slots')
        print('  Type "back"     - return to the main menu')
        choice = input("> ").strip().lower()

        if choice == "timings":
            print("\nOur business hours are:")
            for day, hours in BUSINESS_HOURS.items():
                print(f"  {day}: {hours}")

        elif choice == "walkins":
            if is_walk_in_available():
                window = random.choice(WALK_IN_WINDOWS)
                print(f"\nGood news! Walk-ins are open today from {window}.")
            else:
                print("\nSorry, we are not taking walk-ins today. Please book an appointment instead.")

        elif choice == "checkup":
            slots = get_available_checkup_slots()
            print("\nHere are today's open pet checkup slots:")
            for slot in slots:
                print(f"  - {slot}")
            print('Mention any of these times when you call to reserve it.')

        elif choice == "back":
            print("Returning to the main menu...")
            return

        else:
            print('\nSorry, I did not understand that. Please type "timings", "walkins", "checkup", or "back".')


# ---------------------------------------------------------------------------
# Shared care-menu engine
# ---------------------------------------------------------------------------

def run_care_menu(animal, options):
    print(f"\nHi, I am a {animal} Care Agent.")
    print("Here is what I can help you with:")
    for keyword, info in options.items():
        print(f'  Type "{keyword}" - {info["label"]}')
    print('  Type "back" - return to the main menu')

    while True:
        choice = input("How can I assist you? ").strip().lower()

        if choice == "back":
            print("Returning to the main menu...")
            return
        elif choice in options:
            print(options[choice]["response"])
            print('Need anything else? Pick another option above, or type "back" to leave.')
        else:
            valid = ", ".join(f'"{k}"' for k in options)
            print(f'I do not understand that request. Please choose from: {valid}, or "back".')


# ---------------------------------------------------------------------------
# Cat care
# ---------------------------------------------------------------------------

CAT_OPTIONS = {
    "treatment": {
        "label": "basic treatment plans for common ailments",
        "response": "I can provide you with a basic treatment plan for your cat, including at-home care tips and signs that mean you should see a vet in person.",
    },
    "grooming": {
        "label": "grooming tips (brushing, nails, bathing)",
        "response": "I can provide you with grooming tips for your cat, such as how often to brush, how to trim nails safely, and when (rarely) a bath is needed.",
    },
    "health": {
        "label": "general health and wellness checklist",
        "response": "I can provide you with a checklist to keep your cat healthy, covering diet, exercise, dental care, and regular vet visits.",
    },
    "diet": {
        "label": "nutrition and feeding guidance",
        "response": "I can provide you with feeding guidance, including portion sizes by age and weight, and foods that are toxic to cats.",
    },
    "vaccination": {
        "label": "vaccination schedule information",
        "response": "I can provide you with information about core and non-core vaccinations and how often your cat needs booster shots.",
    },
    "behavior": {
        "label": "behavior and litter box tips",
        "response": "I can provide you with tips for common behavior issues, like litter box avoidance, scratching furniture, or excessive meowing.",
    },
    "price": {
        "label": "estimated pricing for services",
        "response": "I can give you an estimated price range. Routine checkups typically run $40-$75, and vaccinations run $20-$35 each.",
    },
}


def catcare():
    run_care_menu("Cat", CAT_OPTIONS)


# ---------------------------------------------------------------------------
# Dog care
# ---------------------------------------------------------------------------

DOG_OPTIONS = {
    "treatment": {
        "label": "basic treatment plans for common ailments",
        "response": "I can provide you with a basic treatment plan for your dog, including at-home care tips and signs that mean you should see a vet in person.",
    },
    "grooming": {
        "label": "grooming tips (brushing, nails, bathing)",
        "response": "I can provide you with grooming tips for your dog, including brushing frequency by coat type, nail trims, and bathing schedules.",
    },
    "health": {
        "label": "general health and wellness checklist",
        "response": "I can provide you with a checklist to keep your dog healthy, covering diet, exercise, dental care, and regular vet visits.",
    },
    "diet": {
        "label": "nutrition and feeding guidance",
        "response": "I can provide you with feeding guidance, including portion sizes by breed and age, and foods that are toxic to dogs.",
    },
    "vaccination": {
        "label": "vaccination schedule information",
        "response": "I can provide you with information about core and non-core vaccinations and how often your dog needs booster shots.",
    },
    "training": {
        "label": "basic training and behavior tips",
        "response": "I can provide you with basic training tips, such as house training, leash manners, and dealing with excessive barking.",
    },
    "price": {
        "label": "estimated pricing for services",
        "response": "I can give you an estimated price range. Routine checkups typically run $45-$80, and vaccinations run $20-$40 each.",
    },
}


def dogcare():
    run_care_menu("Dog", DOG_OPTIONS)


# ---------------------------------------------------------------------------
# Fish care
# ---------------------------------------------------------------------------

FISH_OPTIONS = {
    "treatment": {
        "label": "basic treatment plans for common ailments",
        "response": "I can provide you with a basic treatment plan for your fish, including how to treat common issues like ich or fin rot.",
    },
    "supplements": {
        "label": "extra supplements and water conditioners",
        "response": "I can provide you with information about supplements, such as water conditioners, electrolytes, and vitamin additives.",
    },
    "health": {
        "label": "general health and wellness checklist",
        "response": "I can provide you with a checklist to keep your fish healthy, covering feeding, tank cleanliness, and signs of stress.",
    },
    "tank": {
        "label": "tank setup and maintenance tips",
        "response": "I can provide you with tank setup tips, including sizing, filtration, and how often you should do water changes.",
    },
    "feeding": {
        "label": "feeding schedule and portion guidance",
        "response": "I can provide you with feeding guidance, including how often to feed and how to avoid overfeeding your fish.",
    },
    "water": {
        "label": "water quality and testing tips",
        "response": "I can provide you with tips on testing and maintaining water quality, including pH, ammonia, and temperature ranges.",
    },
    "price": {
        "label": "estimated pricing for services",
        "response": "I can give you an estimated price range. Water quality testing typically runs $15-$30, and treatment plans vary by condition.",
    },
}


def fishcare():
    run_care_menu("Fish", FISH_OPTIONS)


# ---------------------------------------------------------------------------
# Bird care
# ---------------------------------------------------------------------------

BIRD_OPTIONS = {
    "treatment": {
        "label": "basic treatment plans for common ailments",
        "response": "I can provide you with a basic treatment plan for your bird, including at-home care tips and signs that mean you should see a vet in person.",
    },
    "toys": {
        "label": "toy and enrichment recommendations",
        "response": "I can provide you with information about safe toys and enrichment activities to keep your bird mentally stimulated.",
    },
    "health": {
        "label": "general health and wellness checklist",
        "response": "I can provide you with a checklist to keep your bird healthy, covering diet, exercise, and regular vet visits.",
    },
    "diet": {
        "label": "nutrition and feeding guidance",
        "response": "I can provide you with feeding guidance, including seed-to-pellet ratios, safe fruits and veggies, and foods to avoid.",
    },
    "cage": {
        "label": "cage setup and cleaning tips",
        "response": "I can provide you with cage setup tips, including sizing, perch placement, and a recommended cleaning schedule.",
    },
    "feathers": {
        "label": "feather and molting care",
        "response": "I can provide you with tips on feather care, including molting cycles and signs of feather plucking that need attention.",
    },
    "price": {
        "label": "estimated pricing for services",
        "response": "I can give you an estimated price range. Routine checkups typically run $40-$70, and wing/nail trims run $15-$25.",
    },
}


def birdcare():
    run_care_menu("Bird", BIRD_OPTIONS)


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    phone = input("Please enter who you want to call: ")
    if phone != "123 4567":
        print("The person you are trying to reach is currently unavailable.")
        return

    print("Welcome to the Pet Care!")

    while True:
        print("\nWhat would you like to do?")
        print('  Type "agent" - speak with a pet care agent')
        print('  Type "other" - hear about timings, walk-ins, or checkups')
        print('  Type "exit"  - leave the program')
        summonag = input("> ").strip().lower()

        if summonag == "agent":
            print("\nWhich agent would you like to speak with?")
            print("  1. Cat Care")
            print("  2. Dog Care")
            print("  3. Fish Care")
            print("  4. Bird Care")
            print("  5. Back to main menu")
            choice = input("Enter a number: ").strip()

            if choice == "1":
                catcare()
            elif choice == "2":
                dogcare()
            elif choice == "3":
                fishcare()
            elif choice == "4":
                birdcare()
            elif choice == "5":
                continue
            else:
                print("Invalid choice. Please enter a number from 1-5.")

        elif summonag == "other":
            other_info()

        elif summonag == "exit":
            print("Thank you for using the Pet Care program. Goodbye!")
            break

        else:
            print('Invalid selection. Please type "agent", "other", or "exit".')


if __name__ == "__main__":
    main()
