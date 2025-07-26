import cv2
import mediapipe as mp
import random

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

finger_tips = [8, 12, 16, 20]

#Detects whether the hand read by the camera is the right or left hand."
def get_hand_label(hand_landmarks):
    wrist_x = hand_landmarks.landmark[0].x
    thumb_x = hand_landmarks.landmark[1].x
    if thumb_x < wrist_x:
        return "Left"
    else:
        return "Right"

#Determines the hand's gesture or position based on specific points on the fingers.
def detect_gesture(hand_landmarks, hand_label):
    fingers = []

    if hand_label == "Right": #Determines whether the thumb is extended based on the hand's orientation.
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
    elif hand_label == "Left":
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
    else:
        fingers.append(0)

    for tip in finger_tips: #Determines if the remaining fingers are open.
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [0, 0, 0, 0, 0]:
        return "Rock"
    elif fingers == [1, 1, 1, 1, 1]:
        return "Paper"
    elif fingers == [0, 1, 1, 0, 0]:
        return "Scissor"
    else:
        return "Undefined"

#Compares the player's choice with the computer's choice.
def compare(player,computer):
    if player == computer:
        return "Draw"
    elif (player == "Rock" and computer == "Scissor") or \
         (player == "Paper" and computer == "Rock") or \
         (player == "Scissor" and computer == "Paper"):
        return "The player won this round"
    else:
        return "The computer won this round"

player_score = 0
computer_score = 0
game_started = False
font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

        #This is the game start screen where the start command is given.
    if not game_started:
        player_score = 0
        computer_score = 0
        cv2.putText(frame , "Press 's' to start the game",(50,50),font,0.8,(255, 255, 255), 2)
        cv2.imshow("Rock-Paper-Scissor", frame)
        key = cv2.waitKey(1)
        if key == ord('s'):  
            game_started = True
        elif key == ord('q'):
            break
        continue

    #This is the section where the operations for the current round are performed.
    cv2.putText(frame , "Press 'space' to continue the game",(40,60),font,0.8,(255, 255, 255), 2)
    key = cv2.waitKey(1)
    if key == 32:
        for i in range(3, 0, -1):
            _, frame = cap.read()
            cv2.putText(frame, f"{i}", (250, 250), font, 4, (0, 0, 255), 4)
            cv2.imshow("Rock-Paper-Scissor", frame)
            cv2.waitKey(1000) 

        _, gesture_frame = cap.read()
        image = cv2.cvtColor(gesture_frame, cv2.COLOR_BGR2RGB)
        result = hands.process(image)

        gesture = "Undefined"
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_label = get_hand_label(hand_landmarks)
                gesture = detect_gesture(hand_landmarks, hand_label)
                cv2.putText(frame, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
        computer_move = random.choice(["Rock", "Paper", "Scissor"])
        result_text = compare(gesture, computer_move)        
        
        if result_text == "The player won this round":
                player_score += 1
        elif result_text == "The computer won this round":
                computer_score += 1

        cv2.putText(gesture_frame, f"You: {gesture} | Computer: {computer_move}", (10, 100), font, 0.7, (255, 255, 0), 2)
        cv2.putText(gesture_frame, result_text, (10, 140), font, 1, (0, 255, 0), 2)
        cv2.putText(gesture_frame, f"Score - You: {player_score} | Computer: {computer_score}", (10, 180), font, 0.7, (0, 255, 255), 2)
        cv2.imshow("Rock-Paper-Scissor", gesture_frame)
        cv2.waitKey(3000)
        
        #The first to reach 3 points wins, and the game returns to the start screen.
        if player_score == 3 or computer_score == 3:
            winner = "You Win!" if player_score == 3 else "Computer Wins!"
            _, final_frame = cap.read()
            cv2.putText(final_frame, winner, (100, 250), font, 1.5, (0, 0, 255), 3)
            cv2.imshow("Rock-Paper-Scissor", final_frame)
            cv2.waitKey(5000)
            game_started = False
            continue

    cv2.putText(frame, f"Score - You: {player_score} | Computer: {computer_score}", (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.imshow("Rock-Paper-Scissor", frame)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

