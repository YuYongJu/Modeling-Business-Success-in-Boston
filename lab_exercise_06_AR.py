# LAB EXERCISE 06
### SET UP BEGINS Do not modify
section_A = [85, 88, 90, 92, 87, 91, 89, 84, 86, 90]
section_B = [78, 95, 82, 88, 91, 73, 99, 85, 77, 94]
### SET UP ENDS Do not modify

# 1) Write a function called find_average() that takes a list of
# numbers and returns the mean of the list.
def find_average(nums):
    """Returns mean of list of numbers
    Parameters: nums (list): list of numbers
    Returns: mean (float): mean of list"""
    mean = sum(nums) / len(nums)
    return mean

# 2) Write a function called find_median() that takes a list of
#  numbers and returns the median of the list.
def find_median(nums):
    """Returns median of list of numbers
    Parameters: nums (list): list of numbers
    Returns: median (int): median of list"""
    nums.sort()

    n = len(nums)
    mid_index = n // 2

    if n % 2 == 0:
        median = (nums[mid_index - 1] + nums[mid_index]) / 2
    else:
        median = nums[mid_index]

    return median

# 3) Write a function called find_mode() that takes a list of numbers and returns the mode of the list.
# If there are multiple modes, the function should return all of them in a list.
# If there is no mode, the function should return the original list of numbers
def find_mode(nums):
    """Returns mode of list of numbers. If multiple modes, returns all of them in a list. 
    If no mode, returns original list of nums. 
    Parameters: nums (list): list of numbers
    Returns: mode (int): Mode of list"""
    highest_count = 0
    counts = {}
    modes = []
    nums_sorted = sorted(nums)

    for num in nums_sorted:
        counts[num] = counts.get(num, 0) + 1
    for count in counts.values():
        if count > highest_count:
            highest_count = count
    if highest_count == 1 and len(nums_sorted) > 1:
        return nums
    for num, count in counts.items():
        if count == highest_count:
            modes.append(num)

    if len(modes) == 1:
        return modes[0]
    return modes


# 4) Write a function called find_variance() that takes a list of
# numbers and returns the population variance of the list.
def find_variance(nums):
    """Calculates population variance for list of numbers
    Parameters: nums (list): list of numbers
    Returns: variance (float): Population variance for nums"""
    mean = find_average(nums)
    variance = sum((num - mean) ** 2 for num in nums) / len(nums)
    return variance

# Write a function called find_sd() that takes variance and
# returns the standard deviation.
def find_sd(var):
    """Uses variance to calculate standard deviation
    Parameters: var (float): population variance for list of nums
    Returns: sd (float): standard deviation calculated"""
    sd = var ** .5
    return sd

# 5) Using the funcs created, calculate the following for section_A and section_B:
# mean, median, mode(s), population variance and its standard deviation
mean_A = find_average(section_A)
mean_B = find_average(section_B)

median_A = find_median(section_A)
median_B = find_median(section_B)

mode_A = find_mode(section_A)
mode_B = find_mode(section_B)

var_A = find_variance(section_A)
var_B = find_variance(section_B)

sd_A = find_sd(var_A)
sd_B = find_sd(var_B)

def main():
    # 1) Average
    print("Section A Average: ", mean_A)
    print("Section B Average: ", mean_B)
    
    # 2) Median
    print("Section A Median: ", median_A)
    print("Section B Median: ", median_B)
    
    # 3) Mode
    print("Section A Mode: ", mode_A)
    print("Section B Mode: ", mode_B)
    
    # 4) Variance
    print("Section A Variance: ", var_A)
    print("Section B Variance: ", var_B)

    # Standard Deviation
    print("Section A SD: ", sd_A)
    print("Section B SD: ", sd_B)

if __name__ == '__main__':
    main()