import cv2
import numpy as np

def display_lines(img, lines, line_length_factor=0.5):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            if line is not None:
                for x1, y1, x2, y2 in line:
                    dx = x2 - x1
                    dy = y2 - y1
                    line_length = np.sqrt(dx ** 2 + dy ** 2)
                    shortened_length = line_length * line_length_factor
                    angle = np.arctan2(dy, dx)
                    x1_new = int(x1 + shortened_length * np.cos(angle) / 2)
                    y1_new = int(y1 + shortened_length * np.sin(angle) / 2)
                    x2_new = int(x2 - shortened_length * np.cos(angle) / 2)
                    y2_new = int(y2 - shortened_length * np.sin(angle) / 2)
                    cv2.line(line_image, (x1_new, y1_new), (x2_new, y2_new), (0, 0, 255), 10)
    return line_image



def canny(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = 5
    canny = cv2.Canny(gray, 50, 150)
    return canny


    return line_image

def region_of_interest(canny):
    height, width = canny.shape[:2]
    mask = np.zeros_like(canny)
    triangle = np.array([
        (width // 4, height),
        (width // 2, height // 2),
        (width * 3 // 4, height),
    ], np.int32)
    cv2.fillPoly(mask, [triangle], 255)
    masked_image = cv2.bitwise_and(canny, mask)
    return masked_image

def houghLines(cropped_canny):
    return cv2.HoughLinesP(cropped_canny, 1, np.pi / 180, threshold=100, minLineLength=40, maxLineGap=5)

def addWeighted(frame, line_image):
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)

def make_points(image, line):
    slope, intercept = line
    y1 = int(image.shape[0])
    y2 = int(y1 * 3.0 / 5)
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return [[x1, y1, x2, y2]]

def average_slope_intercept(image, lines):
    if lines is None:
        return None
    
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        fit = np.polyfit((x1, x2), (y1, y2), 1)
        slope = fit[0]
        intercept = fit[1]
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
    
    left_line = None
    if len(left_fit) > 0:
        left_fit_average = np.average(left_fit, axis=0)
        left_line = make_points(image, left_fit_average)
    
    right_line = None
    if len(right_fit) > 0:
        right_fit_average = np.average(right_fit, axis=0)
        right_line = make_points(image, right_fit_average)
    
    averaged_lines = [left_line, right_line]
    return averaged_lines

cap = cv2.VideoCapture("test5.mp4")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    canny_image = canny(frame)
    cropped_canny = region_of_interest(canny_image)

    lines = houghLines(cropped_canny)
    averaged_lines = average_slope_intercept(frame, lines)
    line_image = display_lines(frame, averaged_lines)
    combo_image = addWeighted(frame, line_image)
    cv2.imshow("result", combo_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
