import streamlit as st
import requests

BASE_URL = "http://localhost:8000"
st.title("Lambda Function Platform")

# Track if a change occurred to trigger refresh
if "refresh" not in st.session_state:
    st.session_state.refresh = True

# Load functions into session state if needed
def load_functions():
    res = requests.get(f"{BASE_URL}/functions/")
    if res.ok:
        st.session_state.functions = res.json()
    else:
        st.session_state.functions = {}

if st.session_state.refresh:
    load_functions()
    st.session_state.refresh = False

tab1, tab2, tab3, tab4 = st.tabs([
    "Execute Ad-hoc Code", "Manage Functions", "Add Function", "Execute Stored Function"
])

# -------------------- TAB 1: Ad-hoc Execution --------------------
with tab1:
    st.subheader("Run Ad-hoc Code")
    code = st.text_area("Function Code", key="adhoc_code")
    language = st.selectbox("Language", ["python", "javascript"], key="adhoc_lang")
    timeout = st.slider("Timeout", 1, 10, 5, key="adhoc_timeout")
    runtime = st.selectbox("Runtime", ["runc", "runsc"], key="adhoc_runtime")
    args = st.text_input("Call your function (e.g. my_function(5))", key="adhoc_args")

    if st.button("Run Code", key="run_adhoc"):
        payload = {
            "code": code,
            "language": language,
            "timeout": timeout,
            "runtime": runtime,
            "args": args
        }
        res = requests.post(f"{BASE_URL}/execute", json=payload)
        st.json(res.json())

# -------------------- TAB 2: Manage Functions --------------------
with tab2:
    st.subheader("Manage Functions")
    functions = st.session_state.get("functions", {})
    for fid, meta in functions.items():
        st.markdown(f"**{meta['name']}** - {meta['language']} at `{meta['route']}`")

        with st.expander(f"Edit {meta['name']}"):
            new_name = st.text_input("Function Name", value=meta["name"], key=f"name_{fid}")
            new_route = st.text_input("Route", value=meta["route"], key=f"route_{fid}")
            new_lang = st.selectbox("Language", ["python", "javascript"],
                                    index=["python", "javascript"].index(meta["language"]),
                                    key=f"lang_{fid}")
            new_timeout = st.slider("Timeout", 1, 10, value=meta["timeout"], key=f"timeout_{fid}")
            new_code = st.text_area("Function Code", value=meta.get("code", ""), key=f"code_{fid}")

            if st.button("Update", key=f"update_{fid}"):
                update_payload = {
                    "name": new_name,
                    "route": new_route,
                    "language": new_lang,
                    "timeout": new_timeout,
                    "code": new_code
                }
                res = requests.put(f"{BASE_URL}/functions/{fid}", json=update_payload)
                if res.ok:
                    st.success("Function updated.")
                    st.session_state.refresh = True
                    st.rerun()

                else:
                    st.error("Update failed.")

        if st.button(f"Delete {fid}", key=f"delete_{fid}"):
            del_res = requests.delete(f"{BASE_URL}/functions/{fid}")
            if del_res.ok:
                st.success("Function deleted.")
                st.session_state.refresh = True
                st.rerun()

            else:
                st.error("Error deleting function")

# -------------------- TAB 3: Add New Function --------------------
with tab3:
    st.subheader("Register New Function")
    name = st.text_input("Function Name", key="add_name")
    route = st.text_input("Route", key="add_route")
    lang = st.selectbox("Language", ["python", "javascript"], key="add_lang")
    timeout = st.number_input("Timeout", 1, 10, 5, key="add_timeout")
    code = st.text_area("Function Code", height=100, key="add_code")

    if st.button("Add Function", key="add_func"):
        meta = {
            "name": name,
            "route": route,
            "language": lang,
            "timeout": timeout,
            "code": code
        }
        res = requests.post(f"{BASE_URL}/functions/", json=meta)
        if res.ok:
            st.success("Function added.")
            st.session_state.refresh = True
            st.rerun()
        else:
            st.error("Error adding function")

# -------------------- TAB 4: Execute Stored Function --------------------
with tab4:
    st.subheader("Execute Stored Function")
    functions = st.session_state.get("functions", {})
    func_list = list(functions.items())
    if func_list:
        selected_index = st.selectbox("Select a function", options=list(range(len(func_list))),
                                      format_func=lambda i: func_list[i][1]['name'])
        fid, meta = func_list[selected_index]

        st.code(meta["code"])
        runtime = st.selectbox("Runtime", ["runc", "runsc"], key="stored_runtime")
        args = st.text_input("Call (e.g. my_function(4))", key="stored_args")

        if st.button("Run Function", key="exec_stored"):
            payload = {
                "language": meta["language"],
                "timeout": meta["timeout"],
                "runtime": runtime,
                "args": args
            }
            res = requests.post(f"{BASE_URL}/functions/{fid}/execute", json=payload)
            st.json(res.json())
