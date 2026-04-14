def make_new_category(expenses):
    name = input("What is the name of the category of expenses? ").strip()
    expenses[name] = {}
    return expenses


def new_input(expenses):
    cat = input("Which category does your expense belong to? ").strip()

    if cat not in expenses:
        ans = input("Category is not defined, do you want to make new category? ").strip().lower()
        if ans == "yes":
            expenses[cat] = {}
        else:
            print("Expense was not added.")
            return expenses

    des = input("Please insert your description, or 0: ").strip()
    amount = float(input("How much did you spend? "))

    if des in expenses[cat]:
        expenses[cat][des] += amount
    else:
        expenses[cat][des] = amount

    return expenses


def display(expenses, ans):
    if ans == 2:
        print(expenses)
    else:
        tot = 0
        for cat in expenses:
            for sub in expenses[cat]:
                tot += expenses[cat][sub]
        print("Total:", tot)


def main():
    expenses = {}
    stat = True

    while stat:
        ans = int(input(
            "Enter a number: \n"
            " 1. Add expense \n"
            " 2. View expenses \n"
            " 3. Show total \n"
            " 4. Make new category \n"
            " 5. Exit \n "
        ))

        if ans == 1:
            new_input(expenses)
        elif ans == 2:
            display(expenses, ans)
        elif ans == 3:
            display(expenses, ans)
        elif ans == 4:
            make_new_category(expenses)
        elif ans == 5:
            stat = False
        else:
            print("Error, number not defined")


if __name__ == "__main__":
    main()