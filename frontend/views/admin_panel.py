import streamlit as st
from datetime import datetime, date, time

from services.admin_service import (
    get_all_users,
    get_user_schedule,
    update_user_energy,
    create_user_task,
    update_task,
    delete_task,
)

token = st.session_state.get("token")
user = st.session_state.get("user")
if not token or not user or user.get("role") != "admin":
    st.warning("Admin access required.")
    st.stop()

st.title("Admin Panel")

# --- load users ---
try:
    all_users = get_all_users(token)
except Exception as e:
    st.error(f"Failed to load users: {e}")
    st.stop()

non_admin_users = [u for u in all_users if u.get("role") != "admin"]

if not non_admin_users:
    st.info("No users found.")
    st.stop()

# --- user list ---
st.subheader("Users")

user_options = {u["id"]: f"{u['username']}  (energy: {u['current_energy']:.1f})" for u in non_admin_users}
selected_user_id = st.selectbox(
    "Select a user",
    options=list(user_options.keys()),
    format_func=lambda uid: user_options[uid],
)

if not selected_user_id:
    st.stop()

# --- load selected user schedule ---
try:
    schedule_data = get_user_schedule(token, selected_user_id)
except Exception as e:
    st.error(f"Failed to load schedule: {e}")
    st.stop()

target_user = schedule_data["user"]
user_tasks = schedule_data["tasks"]

st.divider()

# --- user info + energy management ---
st.subheader(f"{target_user['username']}")

col_info, col_energy = st.columns(2)
with col_info:
    st.metric("Current Mana", f"{target_user['current_energy']:.1f} / 10")
    st.caption(f"Account created: {target_user.get('created_time', 'N/A')}")

with col_energy:
    st.markdown("**Set Mana Level**")
    new_energy = st.slider(
        "Energy",
        min_value=0.0,
        max_value=10.0,
        value=float(target_user["current_energy"]),
        step=0.5,
        key="admin_energy_slider",
        label_visibility="collapsed",
    )
    if st.button("Update Mana", key="btn_update_energy"):
        try:
            update_user_energy(token, selected_user_id, new_energy)
            st.success(f"Mana updated to {new_energy:.1f}")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# --- task list ---
st.subheader("Schedule")

if not user_tasks:
    st.info("This user has no tasks.")
else:
    planned = [t for t in user_tasks if t["status"] == "planned"]
    completed = [t for t in user_tasks if t["status"] == "completed"]

    if planned:
        st.markdown("**Planned**")
        for task in planned:
            sched = task["scheduled_time"].replace("Z", "+00:00")
            dt = datetime.fromisoformat(sched)
            time_str = dt.strftime("%b %d, %I:%M %p")

            with st.expander(f"{task['title']}  —  {time_str}  (cost: {task['energy_cost']:.1f})"):
                if task.get("description"):
                    st.caption(task["description"])

                st.markdown("**Edit Task**")
                new_title = st.text_input("Title", value=task["title"], key=f"title_{task['id']}")
                new_cost = st.slider(
                    "Energy Cost",
                    0.0, 10.0,
                    value=float(task["energy_cost"]),
                    step=0.5,
                    key=f"cost_{task['id']}",
                )
                new_time = st.time_input("Time", value=dt.time(), key=f"time_{task['id']}")
                new_date = st.date_input("Date", value=dt.date(), key=f"date_{task['id']}")

                col_save, col_del = st.columns(2)
                with col_save:
                    if st.button("Save Changes", key=f"save_{task['id']}"):
                        updates = {}
                        if new_title.strip() != task["title"]:
                            updates["title"] = new_title.strip()
                        if new_cost != task["energy_cost"]:
                            updates["energy_cost"] = new_cost
                        scheduled_dt = datetime.combine(new_date, new_time)
                        if scheduled_dt.isoformat() != dt.replace(tzinfo=None).isoformat():
                            updates["scheduled_time"] = scheduled_dt.isoformat()
                        if updates:
                            try:
                                update_task(token, task["id"], updates)
                                st.success("Task updated.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.info("No changes to save.")

                with col_del:
                    if st.button("Delete", key=f"del_{task['id']}", type="primary"):
                        try:
                            delete_task(token, task["id"])
                            st.success("Task deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    if completed:
        st.markdown("**Completed**")
        for task in completed:
            sched = task["scheduled_time"].replace("Z", "+00:00")
            dt = datetime.fromisoformat(sched)
            time_str = dt.strftime("%b %d, %I:%M %p")
            st.markdown(f"~~{task['title']}~~ — {time_str} (cost: {task['energy_cost']:.1f})")

st.divider()

# --- create task for user ---
st.subheader("Add Task for User")

with st.form("admin_create_task", clear_on_submit=True):
    task_title = st.text_input("Task Title")
    task_desc = st.text_input("Description (optional)")
    col_d, col_t = st.columns(2)
    with col_d:
        task_date = st.date_input("Date", value=date.today())
    with col_t:
        task_time = st.time_input("Time", value=time(9, 0))
    task_cost = st.slider("Energy Cost", 0.0, 10.0, value=3.0, step=0.5)
    task_recurring = st.checkbox("Daily recurring")
    submitted = st.form_submit_button("Create Task", use_container_width=True)

if submitted:
    if not task_title.strip():
        st.warning("Task title is required.")
    else:
        scheduled = datetime.combine(task_date, task_time)
        payload = {
            "title": task_title.strip(),
            "description": task_desc.strip(),
            "scheduled_time": scheduled.isoformat(),
            "energy_cost": task_cost,
            "is_recurring": task_recurring,
        }
        if task_recurring:
            payload["repeat_pattern"] = "daily"
        try:
            create_user_task(token, selected_user_id, payload)
            st.success(f"Task '{task_title.strip()}' created for {target_user['username']}.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
