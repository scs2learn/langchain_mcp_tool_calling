from faker import Faker
import csv
import os


def generate_dummy_users(num_users=50, filename='users.csv'):
    fake = Faker()
    users = []

    for _ in range(num_users):
        user = {
            "user_id": fake.unique.random_int(min=1, max=1000),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            "address_1": fake.street_address(),
            "address_2": fake.secondary_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.zipcode(),
            "phone": fake.phone_number(),
            "email": fake.email()
        }
        users.append(user)

    # Write to CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)


if __name__ == "__main__":
    generate_dummy_users()