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

# ======================
# Mac Style Weekly Calendar
# ======================

st.markdown("---")

st.header("📅 Weekly Calendar")
# ----------------------
# 记录当前查看第几周
# ----------------------


if "week_offset" not in st.session_state:

    st.session_state.week_offset = 0


col1,col2,col3 = st.columns([1,3,1])

with col1:

    if st.button("Previous Week"):
        st.session_state.week_offset -= 1

with col3:

    if st.button("Next Week"):
        st.session_state.week_offset += 1


# ----------------------
# 当前周
# ----------------------

if len(df) > 0:

    earliest_date = pd.to_datetime(df["date"]).min()
    today = earliest_date

    df["start_dt"] = pd.to_datetime(df["date"] + " " + df["start"])
    df["end_dt"] = pd.to_datetime(df["date"] + " " + df["end"])

else:

    today = datetime.today()

    # 空数据时给“安全空列”
    df = pd.DataFrame(columns=[
        "date", "start", "end", "restaurant", "status", "user", "notes"
    ])

    df["start_dt"] = pd.Series(dtype="datetime64[ns]")
    df["end_dt"] = pd.Series(dtype="datetime64[ns]")


week_start = (
    today
    - timedelta(days=today.weekday())
    + timedelta(weeks=st.session_state.week_offset)
)

week_end = week_start + timedelta(days=6)


st.subheader(
    f"{week_start:%Y-%m-%d} ~ {week_end:%Y-%m-%d}"
)

# ----------------------
# 日期栏
# ----------------------

week_days = [
    week_start + timedelta(days=i)
    for i in range(7)
]

cols = st.columns(7)

for i, day in enumerate(week_days):

    cols[i].markdown(
        f"""
        <div style="
            text-align:center;
            padding:10px;
            border-radius:10px;
            border:1px solid rgba(150,150,150,0.4);
            background-color:rgba(255,255,255,0.05);
            color:inherit;
        ">
        <b>{day.day}</b><br>
        {day.strftime('%a')}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")

# ----------------------
# 本周预约
# ----------------------

week_df = df[
    (df["start_dt"].notna()) &
    (df["start_dt"].dt.date >= week_start.date()) &
    (df["start_dt"].dt.date <= week_end.date())
]

# ----------------------
# Mobile Friendly Weekly View
# ----------------------

st.markdown("### 🗓 Weekly Schedule")

if week_df.empty:

    st.info("No bookings this week")

else:

    for day in week_days:

        st.markdown("---")

        st.subheader(day.strftime("%A, %Y-%m-%d"))

        day_events = week_df[
            week_df["start_dt"].dt.date == day.date()
        ]

        if day_events.empty:

            st.write("No bookings")

        else:

            for _, event in day_events.iterrows():

                status = (
                    "🟢 Available"
                    if event["status"] == "available"
                    else f"🔴 Booked by {event['user']}"
                )

                notes = event.get("notes", "")

                st.markdown(
                    f"""
                    <div style="
                        padding:15px;
                        border-radius:12px;
                        margin-bottom:10px;
                        border:1px solid rgba(150,150,150,0.4);
                        background-color:rgba(255,255,255,0.05);
                        color:inherit;
                    ">

                    <h4>🍽 {event['restaurant']}</h4>

                    <p>⏰ {event['start']} - {event['end']}</p>

                    <p>📝 {notes}</p>

                    <p>{status}</p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )