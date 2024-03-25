def calculate_caloric_needs():
    weight = float(input("Enter your weight in kg: "))
    height = float(input("Enter your height in cm: "))
    age = int(input("Enter your age in years: "))
    gender = input("Enter your gender (male/female): ").lower()
    print("\nSelect your activity level:")
    print("1. Sedentary (little or no exercise)")
    print("2. Lightly active (light exercise/sports 1-3 days/week)")
    print("3. Moderately active (moderate exercise/sports 3-5 days/week)")
    print("4. Very active (hard exercise/sports 6-7 days a week)")
    print("5. Super active (very hard exercise/sports & physical job)")
    activity_level = int(input("Enter the number corresponding to your activity level: "))
    
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age) if gender == 'male' else 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    tdee = bmr * [1.2, 1.375, 1.55, 1.725, 1.9][activity_level - 1]
    print(f"\nYour estimated daily calorie needs to maintain your current weight is {tdee:.2f} calories.")

def main():
    if input("Do you want to calculate your daily caloric needs? Y/N ").strip().lower() == 'y':
        calculate_caloric_needs()
    
    if input("\nDo you want healthy food recommendations? Y/N ").strip().lower() == 'y':
        goal = input("Do you want to gain, lose, or maintain your weight? (Gain/Lose/Maintain) ").strip().lower()
        if goal not in ['gain', 'lose', 'maintain']:
            print("Invalid input. Please start over and enter 'Gain', 'Lose', or 'Maintain'.")
            return
        focus = input("Do you want to gain muscle, lose fat, or do both? (Muscle/Fat/Both) ").strip().lower() if goal != 'maintain' else 'both'
        recommendations = get_food_recommendations(goal, focus)
        if recommendations:
            print(f"Here are some foods you can eat to {goal} weight and focus on {focus}:")
            for food in recommendations:
                print(f" - {food}")
        else:
            print("Sorry, we don't have recommendations for this specific goal and focus.")
    else:
        print("Okay, feel free to come back if you change your mind!")

if __name__ == "__main__":
    main()



