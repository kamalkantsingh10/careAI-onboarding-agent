from data.db_manager import ConversationDB, CustomerDB


db_customer=CustomerDB()

def call_function(function_name, arguments):
    # This function will dispatch to the appropriate function based on name
    if function_name == "User_Validation":
        return get_user_details(arguments)
    # Add more function handlers as needed
    else:
        return f"Unknown function: {function_name}"

def get_user_details(args):
    # Implementation for User_Validation function
    dob = args.get("Dob")
    user_name = args.get("user_name")
    
    # Your validation logic here
    customers = db_customer.find_by_name_dob(user_name, dob)
    if not customers:
        print(f"No user found with name: {user_name} and date of birth: {dob}")
        return None
    
    customer = customers[0]
    fields = [
        ('Customer ID', 'id'),
        ('Name', 'customer_name'),
        ('DOB', 'date_of_birth'),
        ('Main Goal', 'main_goal'),
        ('Chronic Conditions', 'chronic_conditions'),
        ('Allergies', 'allergies'),
        ('Consent', 'consent'),
        ('Patient Name', 'patient_name'),
        ('Relationship', 'relationship_to_customer'),
        ('Patient Age', 'age'),
        ('Address', 'address'),
        ('2care Interest', 'interested_in_2care')
    ]
    
    # Build output text, skipping empty fields
    lines = []
    for label, key in fields:
        if value := customer.get(key):  # Python 3.8+ assignment expression
            lines.append(f"{label}: {value}")
    
    return "\n".join(lines)