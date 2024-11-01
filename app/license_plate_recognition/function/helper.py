import math


# license plate type classification helper function
def linear_equation(x1, y1, x2, y2):
    b = y1 - (y2 - y1) * x1 / (x2 - x1)
    a = (y1 - b) / x1
    return a, b


def check_point_linear(x, y, x1, y1, x2, y2):
    # Calculate the linear equation coefficients (a, b) for the line passing through (x1, y1) and (x2, y2)
    a, b = linear_equation(x1, y1, x2, y2)
    # Predict the y-coordinate for the given x using the linear equation
    y_pred = a * x + b
    # Check if the predicted y-coordinate is close to the actual y-coordinate within a tolerance of 3
    return math.isclose(y_pred, y, abs_tol=3)


# Detect characters and numbers in the license plate
def read_plate(yolo_license_plate, im):
    LP_type = "1"  # Initialize license plate type as "1" (1-line plate)
    results = yolo_license_plate(im)  # Run the YOLO model on the input image
    bb_list = (
        results.pandas().xyxy[0].values.tolist()
    )  # Get bounding box list from results

    # If no bounding boxes are detected or the number of bounding boxes is not between 7 and 10, return "unknown"
    if len(bb_list) == 0 or len(bb_list) < 7 or len(bb_list) > 10:
        return "unknown"

    center_list = []  # List to store the center points of bounding boxes
    y_sum = 0  # Sum of y-coordinates of bounding box centers

    # Calculate the center points of bounding boxes and update y_sum
    for bb in bb_list:
        x_c = (bb[0] + bb[2]) / 2  # Calculate x-coordinate of the center
        y_c = (bb[1] + bb[3]) / 2  # Calculate y-coordinate of the center
        y_sum += y_c  # Update y_sum
        center_list.append(
            [x_c, y_c, bb[-1]]
        )  # Add center point and label to center_list

    # Find the leftmost and rightmost points in center_list
    l_point = center_list[0]
    r_point = center_list[0]
    for cp in center_list:
        if cp[0] < l_point[0]:
            l_point = cp
        if cp[0] > r_point[0]:
            r_point = cp

    # Check if any center point is not on the line defined by l_point and r_point
    for ct in center_list:
        if l_point[0] != r_point[0]:
            if not check_point_linear(
                ct[0], ct[1], l_point[0], l_point[1], r_point[0], r_point[1]
            ):
                LP_type = "2"  # Set license plate type to "2" (2-line plate)

    # Calculate the mean y-coordinate of bounding box centers
    y_mean = int(y_sum / len(bb_list))
    size = (
        results.pandas().s
    )  # Get the size of the results (not used in the current code)

    # 1 line plates and 2 line plates
    line_1 = []
    line_2 = []
    license_plate = ""
    if LP_type == "2":
        for c in center_list:
            if int(c[1]) > y_mean:
                line_2.append(c)
            else:
                line_1.append(c)
        for l1 in sorted(line_1, key=lambda x: x[0]):
            license_plate += str(l1[2])
        license_plate += "-"
        for l2 in sorted(line_2, key=lambda x: x[0]):
            license_plate += str(l2[2])
    else:
        for l in sorted(center_list, key=lambda x: x[0]):
            license_plate += str(l[2])
    return license_plate
