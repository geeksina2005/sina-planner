# -*- coding: utf-8 -*-
# Sina Planner build helper: run "python setup.py prepare" before npm, "python setup.py patch" after "npx cap add android"
import os, sys, shutil
from PIL import Image, ImageDraw

FILES = {'java/MainActivity.java': 'package com.sina.planner;\n\nimport android.os.Bundle;\nimport com.getcapacitor.BridgeActivity;\n\npublic class MainActivity extends BridgeActivity {\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n        registerPlugin(WidgetBridgePlugin.class);\n        super.onCreate(savedInstanceState);\n    }\n}\n', 'java/WidgetBridgePlugin.java': 'package com.sina.planner;\n\nimport android.content.Context;\nimport android.content.SharedPreferences;\nimport com.getcapacitor.Plugin;\nimport com.getcapacitor.PluginCall;\nimport com.getcapacitor.PluginMethod;\nimport com.getcapacitor.annotation.CapacitorPlugin;\n\n@CapacitorPlugin(name = "WidgetBridge")\npublic class WidgetBridgePlugin extends Plugin {\n    @PluginMethod\n    public void update(PluginCall call) {\n        SharedPreferences.Editor e = getContext().getSharedPreferences("sina_widget", Context.MODE_PRIVATE).edit();\n        e.putString("day", call.getString("day", ""));\n        e.putString("summary", call.getString("summary", ""));\n        e.putString("lines", call.getString("lines", ""));\n        e.putInt("pct", call.getInt("pct", 0));\n        e.apply();\n        SinaWidget.refreshAll(getContext());\n        call.resolve();\n    }\n}\n', 'java/SinaWidget.java': 'package com.sina.planner;\n\nimport android.app.PendingIntent;\nimport android.appwidget.AppWidgetManager;\nimport android.appwidget.AppWidgetProvider;\nimport android.content.ComponentName;\nimport android.content.Context;\nimport android.content.Intent;\nimport android.content.SharedPreferences;\nimport android.widget.RemoteViews;\nimport java.text.SimpleDateFormat;\nimport java.util.Date;\nimport java.util.Locale;\n\npublic class SinaWidget extends AppWidgetProvider {\n    @Override\n    public void onUpdate(Context c, AppWidgetManager m, int[] ids) {\n        for (int id : ids) m.updateAppWidget(id, build(c));\n    }\n\n    public static void refreshAll(Context c) {\n        AppWidgetManager m = AppWidgetManager.getInstance(c);\n        int[] ids = m.getAppWidgetIds(new ComponentName(c, SinaWidget.class));\n        for (int id : ids) m.updateAppWidget(id, build(c));\n    }\n\n    static RemoteViews build(Context c) {\n        SharedPreferences p = c.getSharedPreferences("sina_widget", Context.MODE_PRIVATE);\n        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date());\n        boolean fresh = today.equals(p.getString("day", ""));\n        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_sina);\n        v.setTextViewText(R.id.w_sum, fresh ? p.getString("summary", "") : "روز جدید؛ برای به\u200cروزرسانی برنامه را باز کن");\n        v.setTextViewText(R.id.w_list, fresh ? p.getString("lines", "") : "");\n        v.setProgressBar(R.id.w_bar, 100, fresh ? p.getInt("pct", 0) : 0, false);\n        Intent i = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());\n        PendingIntent pi = PendingIntent.getActivity(c, 0, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);\n        v.setOnClickPendingIntent(R.id.w_root, pi);\n        return v;\n    }\n}\n', 'res/xml/sina_widget_info.xml': '<?xml version="1.0" encoding="utf-8"?>\n<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"\n    android:minWidth="250dp"\n    android:minHeight="110dp"\n    android:targetCellWidth="4"\n    android:targetCellHeight="2"\n    android:updatePeriodMillis="1800000"\n    android:initialLayout="@layout/widget_sina"\n    android:resizeMode="horizontal|vertical"\n    android:widgetCategory="home_screen"\n    android:description="@string/widget_desc" />\n', 'res/mipmap-anydpi-v26/ic_launcher_round.xml': '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n', 'res/mipmap-anydpi-v26/ic_launcher.xml': '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n', 'res/values/ic_launcher_background.xml': '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#000000</color>\n</resources>\n', 'res/values/sina_strings.xml': '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="widget_desc">برنامهٔ امروز و پیشرفت تسک\u200cها</string>\n</resources>\n', 'res/layout/widget_sina.xml': '<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n    android:id="@+id/w_root"\n    android:layout_width="match_parent"\n    android:layout_height="match_parent"\n    android:orientation="vertical"\n    android:padding="14dp"\n    android:layoutDirection="rtl"\n    android:background="@drawable/widget_bg">\n    <TextView\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:text="برنامه\u200cریزی سینا"\n        android:textColor="#ECFAF3"\n        android:textStyle="bold"\n        android:textSize="14sp"\n        android:textAlignment="viewStart" />\n    <TextView\n        android:id="@+id/w_sum"\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:layout_marginTop="2dp"\n        android:textColor="#A9CBC0"\n        android:textSize="12sp"\n        android:textAlignment="viewStart" />\n    <ProgressBar\n        android:id="@+id/w_bar"\n        style="?android:attr/progressBarStyleHorizontal"\n        android:layout_width="match_parent"\n        android:layout_height="6dp"\n        android:layout_marginTop="8dp"\n        android:max="100"\n        android:progressTint="#3ECF9B"\n        android:progressBackgroundTint="#33FFFFFF" />\n    <TextView\n        android:id="@+id/w_list"\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:layout_marginTop="10dp"\n        android:maxLines="6"\n        android:ellipsize="end"\n        android:textColor="#FFFFFF"\n        android:textSize="13sp"\n        android:lineSpacingExtra="3dp"\n        android:textAlignment="viewStart" />\n</LinearLayout>\n', 'res/drawable/widget_bg.xml': '<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <gradient android:startColor="#F20B1513" android:endColor="#F2101A2C" android:angle="315" />\n    <corners android:radius="24dp" />\n</shape>\n'}

def prepare():
    os.makedirs('www', exist_ok=True)
    shutil.copy('index.html', 'www/index.html')
    Image.open('logo.jpg').convert('RGB').resize((192, 192), Image.LANCZOS).save('www/icon-192.png')

def patch():
    base = 'android/app/src/main'
    for rel, text in FILES.items():
        if rel.startswith('java/'):
            dst = os.path.join(base, 'java/com/sina/planner', rel[5:])
        else:
            dst = os.path.join(base, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(text)
    src = Image.open('logo.jpg').convert('RGB')
    lum = src.convert('L').point(lambda v: min(255, int(v * 1.25)))
    for d, s, f in [('mdpi', 48, 108), ('hdpi', 72, 162), ('xhdpi', 96, 216), ('xxhdpi', 144, 324), ('xxxhdpi', 192, 432)]:
        o = os.path.join(base, 'res', 'mipmap-' + d)
        os.makedirs(o, exist_ok=True)
        sq = src.resize((s, s), Image.LANCZOS)
        sq.save(os.path.join(o, 'ic_launcher.png'))
        r = sq.convert('RGBA')
        m = Image.new('L', (s, s), 0)
        ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
        r.putalpha(m)
        r.save(os.path.join(o, 'ic_launcher_round.png'))
        k = int(f * 0.62)
        fg = Image.new('RGBA', (f, f), (0, 0, 0, 0))
        w = Image.new('RGBA', (k, k), (255, 255, 255, 255))
        w.putalpha(lum.resize((k, k), Image.LANCZOS))
        fg.paste(w, ((f - k) // 2, (f - k) // 2), w)
        fg.save(os.path.join(o, 'ic_launcher_foreground.png'))
    p = os.path.join(base, 'AndroidManifest.xml')
    s = open(p, encoding='utf-8').read()
    rcv = """<receiver android:name=".SinaWidget" android:exported="true">
  <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
  <meta-data android:name="android.appwidget.provider" android:resource="@xml/sina_widget_info"/>
</receiver>
"""
    s = s.replace('</application>', rcv + '</application>', 1)
    s = s.replace('</manifest>', '<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>\n<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>\n</manifest>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('patched')

if __name__ == '__main__':
    {'prepare': prepare, 'patch': patch}[sys.argv[1]]()
