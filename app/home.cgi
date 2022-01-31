#!le/usr/bin/env python3
import cgi
import sqlite3
import jinja2
#import logging
#logging.basicConfig(filename='home.log',level=logging.INFO,format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
#logging.info("logging test")

SQLDB = '/home/pi/PILN/db/PiLN.sqlite3'
db = sqlite3.connect(SQLDB) 
db.row_factory = sqlite3.Row
cursor = db.cursor()

env = jinja2.Environment(loader=jinja2.FileSystemLoader(['/home/pi/PILN/template/'])) 

maxsegs = 20
def_rate = 9999
def_holdmin = 0
def_intsec = 30

form = cgi.FieldStorage()
page = form.getfirst("page", "")
run_id = form.getfirst("run_id", "0")
notes = form.getfirst("notes", "")
state = form.getfirst("state", "")

#--- view profile ---#
if page == "view":
    sql = 'SELECT * FROM profiles WHERE run_id=?;'
    p = (int(run_id),)
    cursor.execute(sql, p)
    profile = cursor.fetchone()
    sql = '''SELECT segment, set_temp, rate, hold_min, int_sec, start_time, end_time
               FROM segments WHERE run_id=? ORDER BY segment;
          '''
    p = (int(run_id),)
    cursor.execute(sql, p)
    segments = cursor.fetchall()
    template = env.get_template("header.html") 
    hdr = template.render(title="Profile Details")
    viewtmpl = "view_staged.html"
    if state == "Completed" or state == "Stopped" or state == "Error" :
        viewtmpl = "view_comp.html"
    elif state == "Running":
        viewtmpl = "view_run.html"
    template = env.get_template(viewtmpl) 
    bdy = template.render(segments=segments, profile=profile,
          run_id=run_id, state=state, notes=notes, 
    )
    if state == "Completed" or state == "Running" or state == "Stopped":
        template = env.get_template("chart.html") 
        bdy += template.render(run_id=run_id, notes=notes)
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- new profile ---#
elif page == "new":
    segments = range(1,maxsegs + 1)

    template = env.get_template("header.html") 
    hdr = template.render(title="New Profile")
    template = env.get_template("new.html") 
    bdy = template.render(segments=segments)
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- editcopy ---#
elif page == "editcopy":
    sql = '''SELECT segment, set_temp, rate, hold_min, int_sec
                         FROM segments WHERE run_id=?    ORDER BY segment;
                '''
    p = (int(run_id),)
    cursor.execute(sql, p)
    segments = cursor.fetchall()
    curcount = len(segments)
    addsegs = range(curcount+1, maxsegs+1)
    lastseg = curcount

    sql = 'SELECT notes, p_param, i_param, d_param FROM profiles WHERE run_id=?;'
    p = (int(run_id),)
    cursor.execute(sql, p)
    profile = cursor.fetchone()

    template = env.get_template("header.html") 
    hdr = template.render(title="Edit/Copy Profile")
    template = env.get_template("editcopy.html") 
    bdy = template.render( segments=segments, addsegs=addsegs, lastseg=lastseg,
        run_id=run_id, profile=profile, state=state, notes=notes
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- run profile ---#
elif page == "run":
    template = env.get_template("header.html") 
    hdr = template.render(title="Run Profile")

    sql = 'SELECT run_id FROM profiles WHERE state=?;'
    p = ('Running',)
    cursor.execute(sql, p)
    runningid = cursor.fetchone()
    if runningid:
        message = "Unable start profile - Profile %d already running" % int(runningid['run_id'])
        template = env.get_template("reload.html") 
        bdy = template.render( target_page = "view", timeout = 5000,
              message = message,
              params = {"run_id": run_id, "state":"Staged", "notes": notes}
        )
    else:
        sql = 'UPDATE profiles SET state=? WHERE run_id=?;'
        p = ('Running', int(run_id))
        cursor.execute(sql, p)
        db.commit()
        template = env.get_template("reload.html") 
        bdy = template.render(target_page = "view", timeout = 800,
              message = "Updating profile to running state...",
              params = {"run_id": run_id, "state":"Running", "notes": notes}
        )

    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- save or update profile ---#
elif page == "savenew" or page == "saveupd":
    p_param = form.getfirst("Kp", 0.000)
    i_param = form.getfirst("Ki", 0.000)
    d_param = form.getfirst("Kd", 0.000)

    if page == "savenew":
        sql = '''INSERT INTO profiles (state, notes, p_param, i_param, d_param)
                               VALUES (?,?,?,?,?);
              '''
        p = ('Staged', notes, float(p_param), float(i_param), float(d_param))
        cursor.execute(sql, p)
        run_id = cursor.lastrowid
    elif page == "saveupd":
        sql = '''UPDATE profiles SET notes=?, p_param=?, i_param=?, d_param=?
                  WHERE run_id=?;
              '''
        p = (notes, float(p_param), float(i_param), float(d_param), int(run_id))
        cursor.execute(sql, p)
        sql = 'DELETE FROM segments WHERE run_id=?;'
        p = (int(run_id),)
        cursor.execute(sql, p)

    #--- common for "savenew" and "saveupd" ---
    sql = '''INSERT INTO segments
                (run_id, segment, set_temp, rate, hold_min, int_sec)
                VALUES (?,?,?,?,?,?);
          '''
    mp = ()
    for num in range(1, maxsegs+1):
        seg = str(num)
        set_temp = form.getfirst("set_temp" + seg, "")
        rate = form.getfirst("rate" + seg, "")
        hold_min = form.getfirst("hold_min" + seg, "")
        int_sec = form.getfirst("int_sec" + seg, "")
        if set_temp != "":
            if rate == "":
                rate = def_rate
            if hold_min == "":
                hold_min = def_holdmin 
            if int_sec == "":
                int_sec = def_intsec
            mp += (int(run_id), num, int(set_temp), int(rate), int(hold_min), int(int_sec)),
    cursor.executemany(sql, mp)
    db.commit()

    template = env.get_template("header.html") 
    hdr = template.render(title="Save Profile")
    template = env.get_template("reload.html") 
    bdy = template.render(target_page = "view", timeout = 1000,
            message = "Saving profile...",
            params = {"state": "Staged", "run_id": run_id, "notes": notes}
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- delete profile confirmation ---#
elif page == "del_conf":
    sql = '''SELECT segment, set_temp, rate, hold_min, int_sec, start_time, end_time
               FROM segments WHERE run_id=? ORDER BY segment;
          '''
    p = (int(run_id),)
    cursor.execute(sql, p)
    segments = cursor.fetchall()
    
    template = env.get_template("header.html") 
    hdr = template.render(title="Confirm Profile Delete")
    template = env.get_template("del_conf.html") 
    bdy = template.render(segments=segments, run_id=run_id,
          notes=notes, state=state
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- delete profile ---#
elif page == "delete":
    sql1 = 'DELETE FROM firing WHERE run_id=?;'
    sql2 = 'DELETE FROM segments WHERE run_id=?;'
    sql3 = 'DELETE FROM profiles WHERE run_id=?;'
    p = (int(run_id),)
    cursor.execute(sql1, p)
    cursor.execute(sql2, p)
    cursor.execute(sql3, p)
    db.commit()

    template = env.get_template("header.html") 
    hdr = template.render(title="Delete Profile")
    template = env.get_template("reload.html") 
    bdy = template.render(target_page = "home", timeout = 1000,
        message = "Deleting profile...", params = {"run_id": run_id}
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- stop ---#
elif page == "stop":
    template = env.get_template("header.html") 
    sql = 'UPDATE profiles SET state=? WHERE run_id=?;'
    p = ('Stopped', int(run_id))
    cursor.execute(sql, p)
    db.commit()

    
    hdr = template.render(title="Stop Profile Run")
    template = env.get_template("reload.html") 
    bdy = template.render(
        target_page = "home",
        timeout = 1000,
        message = "Updating profile...",
        params = {"run_id": run_id}
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- notes_save ---#
elif page == "notes_save":
    sql = 'UPDATE profiles SET notes=? WHERE run_id=?;'
    p = (notes, int(run_id))
    cursor.execute(sql, p)
    db.commit()
 
    template = env.get_template("header.html") 
    hdr = template.render(title="Save Notes")
    template = env.get_template("reload.html") 
    bdy = template.render(target_page = "view", timeout = 0,
        message = "Saving notes...",
        params = {"state": state, "run_id": run_id, "notes": notes}
    )
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

#--- home ---#
else:
    sql =    """SELECT state, run_id, notes, lastdate
                  FROM (SELECT state, run_id, notes, start_time AS lastdate,
                    CASE state
                      WHEN 'Running' THEN 0
                      WHEN 'Staged' THEN 1
                      WHEN 'Stopped' THEN 2
                      WHEN 'Completed' THEN 3
                    END AS blah 
                    FROM profiles
                  ) 
                ORDER BY blah, run_id DESC;"""
    cursor.execute(sql)
    profiles = cursor.fetchall()

    template = env.get_template("header.html") 
    hdr = template.render(title="Profile List")
    template = env.get_template("home.html") 
    bdy = template.render(profiles=profiles)
    template = env.get_template("footer.html") 
    ftr = template.render()
    print (hdr + bdy + ftr)

cursor.close()
db.close()
