import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

FILE_PATH = "schedule.json"

#生成分享码方便别人使用

import random
import string

def generate_share_code():

    return ''.join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=6
        )
    )
    
# ======================
# 数据读写
# ======================

def load_schedule():

    if not os.path.exists(FILE_PATH):

        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_schedule(data):

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ======================
# 创建预约
# ======================

def create_slot(
    date,
    start,
    end,
    restaurant,
    notes
):

    data = load_schedule()

    new_id = len(data) + 1

    share_code = generate_share_code()

    data.append({

        "id": new_id,

        "share_code": share_code,

        "restaurant": restaurant,

        "date": str(date),

        "start": start,

        "end": end,

        "notes": notes,

        "status": "available",

        "user": None

    })

    save_schedule(data)

    return share_code

# ======================
# 预约
# ======================

def book_slot(slot_id,name):

    data = load_schedule()

    for item in data:

        if item["id"] == slot_id:

            if item["status"] == "booked":

                return False

            item["status"] = "booked"

            item["user"] = name

            save_schedule(data)

            return True

    return False


# ======================
# 取消预约
# ======================

def cancel_slot(slot_id):

    data = load_schedule()

    for item in data:

        if item["id"] == slot_id:

            item["status"] = "available"

            item["user"] = None

            save_schedule(data)

            return True

    return False


# ======================
# 页面
# ======================

st.set_page_config(
    page_title="Social Booking Calendar",
    layout="wide"
)

st.title("🍽️ If You Want to Eat with Leah!")

params = st.query_params

share_code = params.get("share")

if share_code:

    data = load_schedule()

    target_slot = None

    for slot in data:

        if slot.get("share_code") == share_code:

            target_slot = slot

            break

    if target_slot:

        st.header("🎉 Booking Page")

        st.write(
            f"Restaurant: {target_slot['restaurant']}"
        )

        st.write(
            f"Date: {target_slot['date']}"
        )

        st.write(
            f"Time: {target_slot['start']} - {target_slot['end']}"
        )

        st.write(
            f"Notes: {target_slot['notes']}"
        )

        guest_name = st.text_input(
            "Your Name"
        )

        if st.button("Book This Slot"):

            if target_slot["status"] == "booked":

                st.error("Already booked")

            else:

                target_slot["status"] = "booked"

                target_slot["user"] = guest_name

                save_schedule(data)

                st.success("Booking Successful!")

        st.stop()

# ======================
# 数据表
# ======================

data = load_schedule()

df = pd.DataFrame(data)

if len(df) > 0:

    st.subheader("Current Schedule")

    display_df = df.copy()

    display_df.index = range(
        1,
        len(display_df) + 1
    )

    st.dataframe(
        display_df[
            [
                "restaurant",
                "date",
                "start",
                "end",
                "status",
                "user"
            ]
        ]
    )

else:

    st.info("No bookings yet")

# ======================
# 创建预约
# ======================

st.sidebar.header("Create Slot")

date = st.sidebar.date_input("Date")

start = st.sidebar.text_input(
    "Start Time",
    "18:00"
)

end = st.sidebar.text_input(
    "End Time",
    "20:00"
)

restaurant = st.sidebar.text_input(
    "Restaurant"
)

notes = st.sidebar.text_area(
    "Notes"
)

#生成分享链接

if st.sidebar.button("Create Slot"):

    code = create_slot(
        date,
        start,
        end,
        restaurant,
        notes
    )

    BASE_URL = "https://eat-with-leah.streamlit.app"

    share_link = (
        f"{BASE_URL}/?share={code}"
    )

    st.sidebar.success(
        "Slot Created!"
    )

    st.sidebar.write(
        "Copy this link:"
    )

    st.sidebar.code(
        share_link
    )


# ======================
# 预约
# ======================

if len(df) > 0:

    available_df = df[
        df["status"]=="available"
    ]

    if len(available_df) > 0:

        st.subheader("Book a Slot")

        slot_id = st.selectbox(
            "Choose Slot",
            available_df["id"]
        )

        name = st.text_input(
            "Your Name"
        )

        if st.button("Book"):

            if book_slot(slot_id,name):

                st.success("Booked!")

                st.rerun()

            else:

                st.error("Already booked")


# ======================
# 取消预约
# ======================

if len(df) > 0:

    booked_df = df[
        df["status"]=="booked"
    ]

    if len(booked_df) > 0:

        st.subheader("Cancel Booking")

        cancel_id = st.selectbox(
            "Booked Slot",
            booked_df["id"]
        )

        if st.button("Cancel"):

            cancel_slot(cancel_id)

            st.success("Cancelled")

            st.rerun()

# ======================
# 删除Slot
# ======================

if len(df) > 0:

    st.subheader("🗑 Delete Slot")

    delete_id = st.selectbox(
        "Choose Slot",
        df["id"],
        key="delete_slot"
    )

    if st.button(
        "Delete Slot"
    ):

        data = load_schedule()

        data = [
            item
            for item in data
            if item["id"] != delete_id
        ]

        save_schedule(data)

        st.success("Deleted!")

        st.rerun()
        
# ======================
# 周历
# ======================

from streamlit_calendar import calendar

st.markdown("---")
st.header("📅 Calendar")

events = []

if len(df) > 0:

    for _, row in df.iterrows():

        if row["status"] == "available":
            color = "#7BD88F"   # 绿色
        else:
            color = "#FF8A80"   # 红色

        events.append(
            {
                "title": f"{row['restaurant']}",
                "start": f"{row['date']}T{row['start']}",
                "end": f"{row['date']}T{row['end']}",
                "backgroundColor": color,
                "borderColor": color,
            }
        )

calendar_options = {
    "initialView": "dayGridMonth",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek"
    },
    "height": 700,
}

calendar(
    events=events,
    options=calendar_options
)