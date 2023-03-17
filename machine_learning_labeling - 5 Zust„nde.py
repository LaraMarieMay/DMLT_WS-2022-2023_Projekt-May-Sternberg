from pymongo import MongoClient
import pandas as pd
import numpy as np

def calcFFT(accel, nrsamples):
    accel_without_mean = accel - np.mean(accel)
    freq = np.fft.rfft(accel_without_mean, nrsamples, norm='ortho')
    freq = np.abs(freq)
    freq = freq / nrsamples
    return freq

client = MongoClient("mongodb+srv://dlsp:dlsp@cluster0.6jkhj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.DLSP
collection = db.Machine_Learning
classification_list = []
accel_ges_list = []
counter_stillstand = 0
counter_spülen = 0
counter_vorwäsche = 0
counter_waschen = 0
counter_schleudern = 0
counter_defekte = 0

df_data = pd.DataFrame(list(collection.find()))
print("Zu klassifizierendes Dataframe: \n", df_data)
start_time = df_data["time"][0]

for i in range(len(df_data)):
    time_scaled = (int(df_data["time"][i][3]) - int(start_time[3])) * 60 * 60 + (
                          int(df_data["time"][i][4]) - int(start_time[4])) * 60 + (
                          int(df_data["time"][i][5]) - int(start_time[5])) + (
                          int(df_data["time"][i][6]) - 0) / 1000
    time_scaled = round(time_scaled, 3)
    Accel_ges = abs(float(df_data["Ax"][i])) + abs(float(df_data["Ay"][i])) + abs(float(df_data["Az"][i]))
    if time_scaled < 0:
        counter_defekte = counter_defekte + 1

    elif time_scaled < 275 or 315 <= time_scaled < 343 or 1215 <= time_scaled < 1271 or 1298 <= time_scaled < 1440 \
            or 8995 <= time_scaled < 9390 or 9709 <= time_scaled:
        classification_list.append(2)  # Spülen
        accel_ges_list.append(Accel_ges)
        counter_spülen = counter_spülen + 1
    elif 352 <= time_scaled < 400 or 408 <= time_scaled < 416 or 426 <= time_scaled < 1130:
        classification_list.append(3)  # Vorwäsche
        accel_ges_list.append(Accel_ges)
        counter_vorwäsche = counter_vorwäsche + 1
    elif 1140 <= time_scaled < 1215 or 8740 <= time_scaled < 8995 or 9480 <= time_scaled < 9709:
        classification_list.append(5)  # Schleudern
        accel_ges_list.append(Accel_ges)
        counter_schleudern = counter_schleudern + 1
    elif 275 <= time_scaled < 315 or 379 <= time_scaled < 388 or 416 <= time_scaled < 425 or 480 <= time_scaled < 490 or 546 <= time_scaled < 556 or 566 <= time_scaled < 575 or 740 <= time_scaled < 749 or 2134 <= time_scaled < 2162 or 8105 <= time_scaled < 8160:
        classification_list.append(1)  # Stillstand
        accel_ges_list.append(Accel_ges)
        counter_stillstand = counter_stillstand + 1
    elif 3889 <= time_scaled < 3915 or 5776 <= time_scaled < 5801 or 6167 <= time_scaled < 6226 or 7213 <= time_scaled < 7239 or 7245 <= time_scaled < 7270 or 7452 <= time_scaled < 7478 or 7483 <= time_scaled < 7508 or 8160 <= time_scaled < 8188 or 8191 <= time_scaled < 8214 or 8470 <= time_scaled < 8538:
        classification_list.append(4)  # Waschen
        accel_ges_list.append(Accel_ges)
        counter_waschen = counter_waschen + 1

df_data = pd.DataFrame({"Accel Gesamt": accel_ges_list, "Classification": classification_list})
print("\n\nÜbersicht der Klassifizierungsergebnisse:")
print("Stillstand: ", counter_stillstand, "\nSpülen: ", counter_spülen, "\nVorwäsche: ", counter_vorwäsche,
      "\nWaschen: ", counter_waschen, "\nSchleudern: ", counter_schleudern, "\nDefekte Datensätze: ", counter_defekte,
      "\n\nKlassifiziertes Dataframe: \n", df_data)

index = 0
column_list = []
row_list = []
insert_list = []
class_list = []
for i in range(51):
    column_list.append(i)
df_train_data = pd.DataFrame(columns=column_list)
while index + 100 < len(df_data):
    class_pass = False
    class_set = df_data["Classification"][index]
    i = index
    j = index
    while i < index + 100:
        i = i + 1
        if not df_data["Classification"][i] == class_set:
            class_pass = True
    if not class_pass:
        while j < index + 100:
            j = j + 1
            row_list.append(df_data["Accel Gesamt"][j])
        freq_values = calcFFT(row_list, len(row_list))
        for value in freq_values:
            insert_list.append(value)
        class_list.append(class_set)
        df_train_data = df_train_data.append([insert_list], ignore_index=True)
        row_list.clear()
        insert_list.clear()
    index = index + 100
df_train_data["Classification"] = class_list
length_train_data = min(max(df_train_data.loc[(df_train_data["Classification"] == 1)].count()), max(df_train_data.loc[(df_train_data["Classification"] == 2)].count()), max(df_train_data.loc[(df_train_data["Classification"] == 3)].count()), max(df_train_data.loc[(df_train_data["Classification"] == 4)].count()), max(df_train_data.loc[(df_train_data["Classification"] == 5)].count()))
df_1 = df_train_data.loc[(df_train_data["Classification"] == 1)][:length_train_data]
df_2 = df_train_data.loc[(df_train_data["Classification"] == 2)][:length_train_data]
df_3 = df_train_data.loc[(df_train_data["Classification"] == 3)][:length_train_data]
df_4 = df_train_data.loc[(df_train_data["Classification"] == 4)][:length_train_data]
df_5 = df_train_data.loc[(df_train_data["Classification"] == 5)][:length_train_data]
df_train_data_final = df_1.append(df_2).append(df_3).append(df_4).append(df_5)
df_train_data_final.to_csv("ML_Train_Data_5_states.csv")
print("\n\nIn CSV-Datei gespeicherte Trainingsdaten: \n", df_train_data_final)
print("Für jede Klasse stehen ", length_train_data, "Reihen für das maschinelle Lernen zur Verfügung")