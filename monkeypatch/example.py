class MyClass:
    def my_function(self):
        return "Original function"

    def patch_my_function(self, new_function):
        # Monkey patch the class function using setattr
        setattr(self, 'my_function', new_function.__get__(self))

    def reset_my_function(self):
        # Reset my_function to the original function defined within the class
        my_function = getattr(self.__class__, "my_function")
        setattr(self, 'my_function', my_function.__get__(self))


# Define the new method to be patched as a method within the class
def new_function(self):
    return f"Patched function called by {self.__class__.__name__}"


# Test the original function
obj = MyClass()
print(obj.my_function())  # Output: "Original function"

# Patch my_function using the class method with the new_function argument
obj.patch_my_function(new_function)

# Test the patched function
print(obj.my_function())  # Output: "Patched function called by MyClass"

# Reset my_function to the original implementation
obj.reset_my_function()

# Test the original function after resetting
print(obj.my_function())  # Output: "Original function"


# class MyClass:
#     def my_function(self):
#         return "Original function"
#
#     def patch_my_function(self, new_function):
#         # Monkey patch the class function using setattr
#         setattr(self, 'my_function', new_function.__get__(self))
#
#
# # Define the new method to be patched as a method within the class
# def new_function(self):
#     return f"Patched function called by {self.__class__.__name__}"
#
#
# # Test the original function
# obj = MyClass()
# print(obj.my_function())  # Output: "Original function"
#
# # Patch my_function using the class method with the new_function argument
# obj.patch_my_function(new_function)
#
# # Test the patched function
# print(obj.my_function())  # Output: "Patched function called by MyClass"
