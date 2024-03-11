def get_diet_recommendations():
    goal = input("Do you want to gain, lose, or maintain weight? Enter gain/lose/maintain: ").lower()
    if goal not in ['gain', 'lose', 'maintain']:
        print("Invalid input. Please enter gain, lose, or maintain.")
        return

    if goal == 'maintain':
        print("For maintaining weight, a balanced diet rich in fruits, vegetables, whole grains, and lean proteins is recommended.")
    else:
        focus = input("Do you want to focus on muscle gain, fat loss, or both? Enter muscle/fat/both: ").lower()
        if focus not in ['muscle', 'fat', 'both']:
            print("Invalid input. Please enter muscle, fat, or both.")
            return
        
        if goal == 'gain':
            if focus == 'muscle':
                print("For muscle gain, focus on a high-protein diet with lean meats, dairy eggs, and legumes, along with strength training.")
            elif focus == 'fat':
                print("Gaining fat is not typically recommened, but focusing on overall weight gain with a balanced diet and perhaps consulting a nutritionist would be beneficial.")
            else:
                print("For muscle gain with minimal fat, increase your protein intake and consider a slight caloric surplus with balanced macros. Strength training is key.")
            
        elif goal == 'lose':
            if focus == 'muscle':
                print("Losing weight while gaining muscle requires a protein-rich diet with a slight caloric deficit and regular strength training.")
            elif focus == 'fat':
                print("For fat loss, focus on a caloric deficit with a balanced diet rich in nutrients. Cardio and strenght exercises are beneficial.")
            else:
                print("For losing fat and gaining muscle, maintain a moderate caloric deficit, high protein intake, and a consistent exercise routine combining strength and cardio")

def get_food_recommendations(goal, focus):
    foods = {
        'gain': {
            'muscle': ["Chicken breast", "Quinoa", "Eggs", "Oats", "Cottage cheese"],
            'fat loss': [], #not recommending foods for fat gain
            'both': ["Lean beef", "Salmon", "Tofu", "Brown rice", "Sweet potatoes"]
        },
        'lose': {
            'muscle': [], #not recommending foods for losing muscle
            'fat_loss': ["Leafy greens", "Berries", "Lean proteins like chicken or fish", "Whole grains", "Legumes"],
            'both': [] #not recommending any
        },
        'maintain': {
            'muscle': ["Turkey", "Legumes", "Whole grains", "Nuts and seeds", "Greek yogurt"],
            'fat_loss': [], #maintenance doesn't typically focus on fat loss
            'both': ["Mixed nuts", "Avocado", "Whole eggs", "Chia seeds", "Lean meats"]
        }
    }
    return foods.get(goal, {}).get(focus, "No specific food recommendations available for this choice.")

def main():
    choice = input("Do you want healthy food recommendations? Y/N ").strip().lower()
    if choice == 'y':
        goal = input("Do you want to gain, lose, or maintain your weight? (Gain/Lose/Maintain) ").strip().lower()
        if goal in ['gain', 'lose', 'maintain']:
            focus = input("Do you want to gain muscle, lose fat, or do both? (Muscle/Fat/Both) ").strip().lower()
            recommendations = get_food_recommendations(goal,focus)
            if recommendations:
                print(f"Here are some foods you can get to {goal} weight and {focus}:")
                for food in recommendations:
                    print(f" - {food}")
            else:
                print("Sorry, we don't have recommendations for this specific goal and focus.")
        else:
            print("Invalid input. Please start over anad enter 'Gain', 'Lose', or 'Maintain'.")
    elif choice == 'n':
        print("Okay, feel free to come back if you change your mind!")
    else:
        print("Invalid input. Please start over and enter 'Y' or 'N'.")

if __name__ == "__main__":
    main()


