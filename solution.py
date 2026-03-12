from playwright.sync_api import sync_playwright
import time


LCA_DATA = {
    "A.1": "H-1B",
    "B.1": "Software Engineer",
    "B.2": "15-1252",
    "B.3": "Software Developers",
    "B.4": "Yes",
    "B.5": "09/10/2026",
    "B.6": "09/09/2029",
    "B.7": "1",
    "B.7a": "1",
    "B.7b": "0",
    "B.7c": "0",
    "B.7d": "0",
    "B.7e": "0",
    "B.7f": "0",
    "C.1": "Test Corporation LLC",
    "C.2": "TestCorp",
    "C.3": "123 Main St",
    "C.5": "New York",
    "C.6": "NEW YORK",
    "C.7": "10001",
    "C.8": "UNITED STATES OF AMERICA",
    "C.10": "5551234567",
    "C.12": "12-3456789",
    "C.13": "541511",
    "D.1": "Contact Last Name",
    "D.2": "Contact First Name",
    "D.3": "",
    "D.4": "HR Manager",
    "D.5": "123 Main St",
    "D.7": "New York",
    "D.8": "NEW YORK",
    "D.9": "10001",
    "D.10": "UNITED STATES OF AMERICA",
    "D.12": "5551234567",
    "D.14": "hr@testcorp.com",
    "E.1": "Attorney",
    "E.2": "Kennedy",
    "E.3": "Adaikala Mary",
    "E.5": "1750 E Golf Rd",
    "E.6": "STE, 1138",
    "E.7": "Schaumburg",
    "E.8": "ILLINOIS",
    "E.9": "60173",
    "E.10": "UNITED STATES OF AMERICA",
    "E.12": "8472201560",
    "E.14": "legal@mkimmigrationlaw.com",
    "E.15": "Law Offices of Mary Kennedy, LLC",
    "E.16": "82-3789282",
    "E.17": "173876",
    "E.18": "OREGON",
    "E.19": "Oregon Supreme Court",
    "F.1": "1",
    "F.2": "No",
    "F.4": "456 Tech Blvd",
    "F.6": "San Francisco",
    "F.7": "San Francisco",
    "F.8": "CALIFORNIA",
    "F.9": "94105",
    "F.10": "130000",
    "F.10a": "Year",
    "F.11": "130000",
    "F.11a": "Year",
    "G.1": "Yes",
    "H.1": "Yes",
    "H.2": "Yes",
    "H.3": "Yes",
    "H.4": "Yes",
    "H.5": "Na",
    "H.6": "Yes",
    "J.1": "Official Last Name",
    "J.2": "Official First Name",
    "J.3": "",
    "J.4": "HR Manager",
    "K.1": "Kennedy",
    "K.2": "Adaikala Mary",
    "K.3": "",
    "K.4": "Law Offices of Mary Kennedy, LLC",
    "K.5": "legal@mkimmigrationlaw.com",
}


def js_fill(page, eid, value):
    if not value:
        return
    v = str(value).replace("\\", "\\\\").replace("'", "\\'")
    page.evaluate(f"""() => {{
        const el = document.getElementById('{eid}');
        if (!el) {{ console.log('NOT FOUND: {eid}'); return; }}
        el.disabled = false;
        el.removeAttribute('disabled');
        const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        s.call(el, '{v}');
        el.dispatchEvent(new Event('input',{{bubbles:true}}));
        el.dispatchEvent(new Event('change',{{bubbles:true}}));
        el.dispatchEvent(new Event('blur',{{bubbles:true}}));
    }}""")


def js_select(page, eid, label):
    if not label:
        return
    v = str(label).replace("'", "\\'")
    page.evaluate(f"""() => {{
        const el = document.getElementById('{eid}');
        if (!el) return;
        el.disabled = false;
        el.removeAttribute('disabled');
        const opt = Array.from(el.options).find(o =>
            o.text.trim().toUpperCase().includes('{v}'.toUpperCase()));
        if (opt) {{ el.value = opt.value; el.dispatchEvent(new Event('change',{{bubbles:true}})); }}
    }}""")


def js_radio(page, eid):
    page.evaluate(f"""() => {{
        const el = document.getElementById('{eid}');
        if (el) {{ el.scrollIntoView(); el.click(); }}
    }}""")


def js_checkbox(page, eid):
    page.evaluate("(id) => { const el = document.getElementById(id); if (el && !el.checked) el.click(); }", eid)


def type_phone(page, eid, number):
    if not number:
        return
    digits = ''.join(c for c in str(number) if c.isdigit())
    try:
        f = page.locator(f"#{eid}")
        f.click()
        f.fill("")
        f.type(digits, delay=100)
        page.keyboard.press("Tab")
    except Exception as e:
        print(f"    phone fallback {eid}: {e}")
        js_fill(page, eid, digits)


def click_continue(page):
    time.sleep(1)
    try:
        page.get_by_role("button", name="Continue").first.click()
    except Exception:
        page.evaluate("""() => {
            const b = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim()==='Continue');
            if (b) b.click();
        }""")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    time.sleep(3)


def get_heading(page):
    try:
        return page.locator("h1").first.text_content().strip()
    except Exception:
        return ""


def section_a(page, d):
    js_radio(page, f"a1_visa_type_{d['A.1']}")


def section_b(page, d):
    js_fill(page, "b1_job_title", d["B.1"])

    soc_input = page.locator('[role="combobox"] input')
    soc_input.click()
    time.sleep(0.5)
    soc_input.type(d["B.2"], delay=150)
    time.sleep(3)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    time.sleep(1)

    js_radio(page, f"b4_is_full_time_{d['B.4']}")
    js_fill(page, "b5_begin_date", d["B.5"])
    js_fill(page, "b6_end_date", d["B.6"])
    js_fill(page, "b7_total_positions", d["B.7"])
    js_fill(page, "b7a_new_employment", d["B.7a"])
    js_fill(page, "b7b_continuation", d["B.7b"])
    js_fill(page, "b7c_change_approved", d["B.7c"])
    js_fill(page, "b7d_new_concurrent", d["B.7d"])
    js_fill(page, "b7e_change_employer", d["B.7e"])
    js_fill(page, "b7f_amended_petition", d["B.7f"])


def section_c(page, d):
    js_fill(page, "c1_emp_name", d["C.1"])
    js_fill(page, "c2_emp_dba", d["C.2"])
    js_fill(page, "c12_emp_fein", d["C.12"])

    try:
        ni = page.locator(".react-autosuggest__container input").first
        ni.click()
        page.keyboard.press("Control+a")
        page.keyboard.press("Backspace")
        ni.type(d["C.13"], delay=200)
        time.sleep(3)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        time.sleep(1)
        print(f"  C.13 NAICS: {d['C.13']}")
    except Exception as e:
        print(f"  C.13 error: {e}")

    js_fill(page, "c3_emp_address_1", d["C.3"])

    # Country FIRST (cascading)
    js_select(page, "c8_emp_country_id", d["C.8"])
    time.sleep(2)
    js_fill(page, "c5_emp_city", d["C.5"])
    js_select(page, "c6_emp_state_id", d["C.6"])
    js_fill(page, "c7_emp_zip", d["C.7"])
    type_phone(page, "c10_emp_phone", d["C.10"])


def section_d(page, d):
    js_fill(page, "d1_poc_last", d["D.1"])
    js_fill(page, "d2_poc_first", d["D.2"])
    if d.get("D.3"): js_fill(page, "d3_poc_middle", d["D.3"])
    js_fill(page, "d4_poc_title", d["D.4"])
    js_fill(page, "d5_poc_address_1", d["D.5"])
    js_select(page, "d10_poc_country_id", d["D.10"])
    time.sleep(2)
    js_fill(page, "d7_poc_city", d["D.7"])
    js_select(page, "d8_poc_state_id", d["D.8"])
    js_fill(page, "d9_poc_zip", d["D.9"])
    type_phone(page, "d12_poc_phone", d["D.12"])
    js_fill(page, "d14_poc_email", d["D.14"])


def section_e(page, d):
    js_radio(page, f"e1_is_represented_{d['E.1']}")
    time.sleep(2)
    js_fill(page, "e2_agent_last", d["E.2"])
    js_fill(page, "e3_agent_first", d["E.3"])
    js_fill(page, "e5_agent_address_1", d["E.5"])
    js_fill(page, "e6_agent_address_2", d.get("E.6", ""))
    js_select(page, "e10_agent_country_id", d["E.10"])
    time.sleep(2)
    js_fill(page, "e7_agent_city", d["E.7"])
    js_select(page, "e8_agent_state_id", d["E.8"])
    js_fill(page, "e9_agent_zip", d["E.9"])
    type_phone(page, "e12_agent_phone", d["E.12"])
    js_fill(page, "e14_agent_email", d["E.14"])
    js_fill(page, "e15_agent_firm_name", d["E.15"])
    js_fill(page, "e16_agent_firm_fein", d["E.16"])
    js_fill(page, "e17_agent_bar_number", d["E.17"])
    js_select(page, "e18_agent_court_state_id", d["E.18"])
    js_fill(page, "e19_agent_court_name", d["E.19"])


def section_f(page, d):
    page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const addBtn = btns.find(b => b.textContent.trim().includes('Add Data'));
        if (addBtn) addBtn.click();
    }""")
    time.sleep(2)


    page.evaluate("""() => {
        const oesRadio = document.querySelector('input[value="f13_is_oes_prevailing_wage"]');
        if (oesRadio) { oesRadio.scrollIntoView(); oesRadio.click(); }
    }""")
    time.sleep(1.5)

    # Step 3: F.2 No, F.4 address, F.6 city, F.9 zip, F.8 state
    page.evaluate(f"""() => {{
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        function setVal(el, val) {{
            if (el) {{ el.disabled = false; setter.call(el, val);
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
                el.dispatchEvent(new Event('change', {{bubbles: true}}));
                el.dispatchEvent(new Event('blur', {{bubbles: true}}));
            }}
        }}
        const f2No = document.querySelector('input[id*="f2_is_secondary_entity_No"]');
        if (f2No) f2No.click();
        setVal(document.querySelector('input[id*="f4_work_address"]'), '{d["F.4"]}');
        setVal(document.querySelector('input[id*="f6_work_city"]'), '{d["F.6"]}');
        setVal(document.querySelector('input[id*="f9_work_zip"]'), '{d["F.9"]}');
        const f8 = document.querySelector('select[id*="f8_work_state"]');
        if (f8) {{ f8.disabled = false; f8.value = '{d["F.8"]}';
            f8.dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
    }}""")
    time.sleep(2)


    try:
        f1 = page.locator('input[id*="f1_number_workers"]').first
        f1.fill(d["F.1"])
        time.sleep(0.5)
    except Exception:
        page.evaluate(f"""() => {{
            const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            const el = document.getElementById('_section_f_f1_number_workers');
            if (el) {{ el.disabled=false; s.call(el,'{d["F.1"]}');
                el.dispatchEvent(new Event('input',{{bubbles:true}}));
                el.dispatchEvent(new Event('change',{{bubbles:true}}));
            }}
        }}""")


    if d.get("F.7"):
        try:
            ci = page.locator("#_section_f_f7_work_county_id")
            ci.click()
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            ci.type(d["F.7"], delay=150)
            time.sleep(3)
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            time.sleep(1)
            print(f"  F.7 County: {d['F.7']}")
        except Exception as e:
            print(f"  F.7 error: {e}")

    page.evaluate(f"""() => {{
        const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        function sn(name,v) {{
            const el = document.querySelector('[name="'+name+'"]');
            if (el) {{ el.disabled=false; s.call(el,v);
                el.dispatchEvent(new Event('input',{{bubbles:true}}));
                el.dispatchEvent(new Event('change',{{bubbles:true}}));
                el.dispatchEvent(new Event('blur',{{bubbles:true}}));
            }}
        }}
        sn('_section_f_f10_nonimmigrant_wage_from','{d["F.10"]}');
        sn('_section_f_f11_prevailing_wage','{d["F.11"]}');
        const f10a = document.getElementById('_section_f_f10a_nonimmigrant_wage_per_{d["F.10a"]}');
        if (f10a) {{ f10a.disabled=false; f10a.click(); }}
        const f11a = document.getElementById('_section_f_f11a_prevailing_wage_per_{d["F.11a"]}');
        if (f11a) {{ f11a.disabled=false; f11a.click(); }}
    }}""")


    page.evaluate("""() => {
        const wl = document.getElementById('_section_f_f13a_wage_level_I');
        if (wl) { wl.disabled=false; wl.removeAttribute('disabled'); wl.click(); }
    }""")

    page.evaluate("""() => {
        const sy = document.getElementById('_section_f_f13b_source_year');
        if (sy) {
            sy.disabled=false; sy.removeAttribute('disabled');
            sy.value = '7/1/2025 - 6/30/2026';
            sy.dispatchEvent(new Event('change',{bubbles:true}));
        }
    }""")
    time.sleep(1)


    clicked = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const addBtn = btns.find(b => b.textContent.trim().includes('Add Place of Employment'));
        if (addBtn && !addBtn.disabled) { addBtn.click(); return true; }
        return false;
    }""")
    time.sleep(3)
    # Verify table shows at least 1 row
    row_count = page.evaluate("""() => {
        const rows = document.querySelectorAll('table tbody tr');
        return rows ? rows.length : 0;
    }""")
    print(f"  F: Place of Employment added (clicked={clicked}, rows={row_count})")


def section_g(page, d):
    js_radio(page, "g1_read_agree_Yes")


def section_h(page, d):
    js_radio(page, f"h1_is_dependent_{d['H.1']}")
    time.sleep(1)
    js_radio(page, f"h2_is_willful_violator_{d['H.2']}")
    time.sleep(1)
    if d.get("H.3"):
        js_radio(page, f"h3_only_h1b_{d['H.3']}")
        time.sleep(1)
    if d.get("H.4"):
        page.evaluate(
            """(v) => {
                const r = document.querySelectorAll('input[type="radio"]');
                for (const x of r) { if (x.id.includes('h4') && x.id.toLowerCase().includes(v.toLowerCase())) { x.click(); return; } }
                for (const x of r) { if (x.id.includes('h4')) { x.click(); return; } }
            }""", d["H.4"])
        time.sleep(1)
    if d.get("H.5"):
        js_radio(page, f"h5_is_appendix_a_completed_{d['H.5']}")
    js_radio(page, f"h6_read_agree_{d['H.6']}")


def section_ij(page, d):
    js_checkbox(page, "Employer's principal place of business")
    js_checkbox(page, "Place of employment")
    js_fill(page, "j1_official_last", d["J.1"])
    js_fill(page, "j2_official_first", d["J.2"])
    if d.get("J.3"): js_fill(page, "j3_official_middle", d["J.3"])
    js_fill(page, "j4_official_title", d["J.4"])


def section_k(page, d):
    js_fill(page, "k1_prep_last", d["K.1"])
    js_fill(page, "k2_prep_first", d["K.2"])
    if d.get("K.3"): js_fill(page, "k3_prep_middle", d["K.3"])
    js_fill(page, "k4_prep_firm_name", d["K.4"])
    js_fill(page, "k5_prep_email", d["K.5"])


def check_errors(page):
    """Check for validation errors on Review page."""
    result = page.evaluate("""() => {
        const alerts = Array.from(document.querySelectorAll('[class*="alert"]'));
        const errors = alerts
            .filter(a => a.offsetParent !== null && a.textContent.toLowerCase().includes('error'))
            .map(a => a.textContent.trim());
        const buttons = Array.from(document.querySelectorAll('button'));
        const submitBtn = buttons.find(b => b.textContent.trim() === 'Submit');
        return {
            errorCount: errors.length,
            errors: errors,
            submitDisabled: submitBtn ? submitBtn.disabled : true
        };
    }""")
    return result


def dismiss_quit_dialog(page):
    """Handle 'Are you sure you want to quit?' dialog by clicking 'Save as Initiated'."""
    time.sleep(2)
    page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const saveBtn = buttons.find(b => b.textContent.trim().includes('Save as Initiated'));
        if (saveBtn) saveBtn.click();
    }""")
    time.sleep(3)


def navigate_to_section(page, section_name):
    """Click sidebar to navigate back to a section + handle quit dialog."""
    page.evaluate("(name) => { const items = Array.from(document.querySelectorAll('li')); "
                  "const target = items.find(li => { const h3 = li.querySelector('h3'); "
                  "return h3 && h3.textContent.includes(name); }); "
                  "if (target) target.click(); }", section_name)
    dismiss_quit_dialog(page)


def click_continue_through_all(page, data):
    """Click Continue through all remaining sections back to Review.
    Stops at Section F to re-add place of employment if table is empty."""
    for i in range(15):
        h = get_heading(page)
        if "Review" in h:
            break

        # If on Section F, check if place of employment exists
        if "Employment and Wage" in h:
            rows = page.evaluate("""() => {
                const r = document.querySelectorAll('table tbody tr');
                return r ? r.length : 0;
            }""")
            if rows == 0:
                print("  Section F table empty — re-adding place of employment")
                section_f(page, data)

        try:
            page.get_by_role("button", name="Continue").first.click()
        except Exception:
            page.evaluate("""() => {
                const b = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim()==='Continue');
                if (b) b.click();
            }""")
        time.sleep(3)


def fix_soc_error(page, data):
    """Fix B.2/B.3 SOC code on Section B."""
    navigate_to_section(page, "Temporary Need")
    soc_input = page.locator('[role="combobox"] input')
    soc_input.click()
    time.sleep(0.5)
    soc_input.type(data["B.2"], delay=150)
    time.sleep(3)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    time.sleep(1)
    print("  Fixed B.2/B.3 SOC")


def fix_naics_error(page, data):
    """Fix C.13 NAICS on Section C."""
    navigate_to_section(page, "Employer Information")
    ni = page.locator(".react-autosuggest__container input").first
    ni.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Backspace")
    ni.type(data["C.13"], delay=200)
    time.sleep(3)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    time.sleep(1)
    print("  Fixed C.13 NAICS")


def fix_section_f_error(page, data):
    """Fix Section F — re-add place of employment."""
    navigate_to_section(page, "Employment and Wage")
    section_f(page, data)
    print("  Fixed Section F")


def review_and_submit(page, data):
    """Automated error-check-solve-submit loop."""
    max_attempts = 5
    for attempt in range(max_attempts):
        status = check_errors(page)
        print(f"\n  Attempt {attempt+1}: {status['errorCount']} errors, submit disabled={status['submitDisabled']}")

        if status['errorCount'] > 0:
            for e in status['errors']:
                print(f"    - {e[:120]}")

        # No errors and submit enabled — submit!
        if status['errorCount'] == 0 and not status['submitDisabled']:
            print("\n  No errors! Submitting...")
            try:
                btn = page.locator("button.usa-button-submission")
                if btn.count() > 0:
                    btn.click()
                else:
                    page.evaluate("""() => {
                        const b = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim()==='Submit');
                        if (b) b.click();
                    }""")
            except Exception:
                page.evaluate("""() => {
                    const b = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim()==='Submit');
                    if (b) b.click();
                }""")
            time.sleep(8)
            print(f"  Post-submit URL: {page.url}")
            if "success" in page.url:
                print("\n  SUCCESS! Application submitted.")
            return

        # No errors but submit still disabled — just wait
        if status['errorCount'] == 0 and status['submitDisabled']:
            print("  No errors but submit disabled. Waiting...")
            time.sleep(5)
            continue

        error_text = ' '.join(status['errors'])

        if 'B.2' in error_text or 'B.3' in error_text:
            fix_soc_error(page, data)
            click_continue_through_all(page, data)
            continue

        if 'C.13' in error_text:
            fix_naics_error(page, data)
            click_continue_through_all(page, data)
            continue

        if 'F:' in error_text or 'at least one' in error_text.lower():
            fix_section_f_error(page, data)
            click_continue_through_all(page, data)
            continue

        print(f"  Unknown errors, clicking Continue through all sections...")
        navigate_to_section(page, "Visa Information")
        click_continue_through_all(page, data)

    print(f"\n  Reached max attempts ({max_attempts}). Check manually.")


def fill_form(data):
    with sync_playwright() as p:
        print("Launching browser...\n")
        ctx = p.chromium.launch_persistent_context(
            user_data_dir="/tmp/flag-playwright-profile",
            headless=False, slow_mo=100,
            viewport={"width": 1400, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Dismiss stale quit modal
        def dismiss():
            try:
                return page.evaluate("""() => {
                    for (const b of document.querySelectorAll('button')) {
                        if (b.textContent.includes('Save as Initiated')) { b.click(); return 'saved'; }
                    }
                    return null;
                }""")
            except: return None

        dismiss()
        time.sleep(1)

        # Navigate to dashboard
        try:
            page.goto("https://flag.dol.gov/dashboard", timeout=60000, wait_until="domcontentloaded")
        except Exception:
            pass
        time.sleep(3)
        dismiss()
        time.sleep(2)

        # If still not on dashboard, retry
        if "flag.dol.gov" not in page.url:
            try:
                page.goto("https://flag.dol.gov/dashboard", timeout=60000, wait_until="domcontentloaded")
            except Exception:
                pass
            time.sleep(3)

        # Login wait
        if "flag.dol.gov" not in page.url:
            print("LOGIN REQUIRED — log in manually. Waiting 10 min...\n")
            t0 = time.time()
            while time.time() - t0 < 600:
                if "flag.dol.gov" in page.url: break
                time.sleep(3)
            if "flag.dol.gov" not in page.url:
                ctx.close(); return
            time.sleep(3)

        dismiss()
        print(f"URL: {page.url}\n")

        # Start new application
        if "/application/9035/" not in page.url:
            try:
                page.locator('a:has-text("Form ETA-9035/9035E")').first.click()
                time.sleep(3)
            except Exception:
                page.evaluate("""() => {
                    const a = Array.from(document.querySelectorAll('a')).find(x => x.textContent.includes('9035'));
                    if (a) a.click();
                }""")
                time.sleep(3)
            dismiss()
            try:
                sb = page.get_by_role("button", name="Start new")
                if sb.is_visible(timeout=5000):
                    sb.click()
                    time.sleep(3)
            except Exception:
                pass
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            time.sleep(3)

        print(f"Application: {page.url}\n")

        # ── Fill sections ────────────────────────────────────────────────
        for _ in range(20):
            h = get_heading(page)
            print(f"\n{'='*50}\n  {h}\n{'='*50}")
            if not h:
                try: click_continue(page)
                except: break
                continue

            if "Visa Information" in h:
                section_a(page, data); click_continue(page)
            elif "Temporary Need" in h:
                section_b(page, data); click_continue(page)
            elif "Employer Information" in h and "Point of Contact" not in h:
                section_c(page, data); click_continue(page)
            elif "Point of Contact" in h:
                section_d(page, data); click_continue(page)
            elif "Attorney" in h or "Agent" in h:
                section_e(page, data); click_continue(page)
            elif "Employment and Wage" in h:
                section_f(page, data); click_continue(page)
            elif "Labor Condition Statements" in h and "H-1B" not in h:
                section_g(page, data); click_continue(page)
            elif "H-1B" in h:
                section_h(page, data); click_continue(page)
            elif "Obligation" in h:
                section_ij(page, data); click_continue(page)
            elif "Preparer" in h:
                section_k(page, data); click_continue(page)
            elif "Appendix" in h or "Document" in h:
                print(f"  (skip)"); click_continue(page)
            elif "Review" in h:
                print(f"\n  REVIEW & SUBMIT")
                review_and_submit(page, data)
                break
            else:
                print(f"  Unknown: {h}")
                try: click_continue(page)
                except: break

        print("\nBrowser stays open. Ctrl+C to exit.")
        try: time.sleep(600)
        except KeyboardInterrupt: pass
        ctx.close()


if __name__ == "__main__":
    print("DOL FLAG LCA Form Filler\n")
    fill_form(LCA_DATA)
