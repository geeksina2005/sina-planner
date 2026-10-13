# -*- coding: utf-8 -*-
# Sina Planner build helper: run "python setup.py prepare" before npm, "python setup.py patch" after "npx cap add android"
import os, sys, shutil
from PIL import Image, ImageDraw

FILES = {'java/MainActivity.java': 'package com.sina.planner;\n\nimport android.os.Bundle;\nimport com.getcapacitor.BridgeActivity;\n\npublic class MainActivity extends BridgeActivity {\n    @Override\n    public void onCreate(Bundle savedInstanceState) {\n        registerPlugin(WidgetBridgePlugin.class);\n        super.onCreate(savedInstanceState);\n    }\n}\n', 'java/WidgetBridgePlugin.java': 'package com.sina.planner;\n\nimport android.content.Context;\nimport android.content.SharedPreferences;\nimport com.getcapacitor.Plugin;\nimport com.getcapacitor.PluginCall;\nimport com.getcapacitor.PluginMethod;\nimport com.getcapacitor.annotation.CapacitorPlugin;\n\n@CapacitorPlugin(name = "WidgetBridge")\npublic class WidgetBridgePlugin extends Plugin {\n    @PluginMethod\n    public void update(PluginCall call) {\n        SharedPreferences.Editor e = getContext().getSharedPreferences("sina_widget", Context.MODE_PRIVATE).edit();\n        e.putString("day", call.getString("day", ""));\n        e.putString("summary", call.getString("summary", ""));\n        e.putString("lines", call.getString("lines", ""));\n        e.putString("img", call.getString("img", ""));\n        e.putString("fin", call.getString("fin", ""));\n        e.putInt("pct", call.getInt("pct", 0));\n        e.apply();\n        SinaWidget.refreshAll(getContext());\n        call.resolve();\n    }\n}\n', 'java/SinaWidget.java': 'package com.sina.planner;\n\nimport android.app.PendingIntent;\nimport android.appwidget.AppWidgetManager;\nimport android.appwidget.AppWidgetProvider;\nimport android.content.ComponentName;\nimport android.content.Context;\nimport android.content.Intent;\nimport android.content.SharedPreferences;\nimport android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\nimport android.util.Base64;\nimport android.widget.RemoteViews;\nimport java.text.SimpleDateFormat;\nimport java.util.Date;\nimport java.util.Locale;\n\npublic class SinaWidget extends AppWidgetProvider {\n    @Override\n    public void onUpdate(Context c, AppWidgetManager m, int[] ids) {\n        for (int id : ids) m.updateAppWidget(id, build(c));\n    }\n\n    public static void refreshAll(Context c) {\n        AppWidgetManager m = AppWidgetManager.getInstance(c);\n        int[] ids = m.getAppWidgetIds(new ComponentName(c, SinaWidget.class));\n        for (int id : ids) m.updateAppWidget(id, build(c));\n    }\n\n    static RemoteViews build(Context c) {\n        SharedPreferences p = c.getSharedPreferences("sina_widget", Context.MODE_PRIVATE);\n        String today = new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date());\n        boolean fresh = today.equals(p.getString("day", ""));\n        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_sina);\n        v.setTextViewText(R.id.w_sum, fresh ? p.getString("summary", "") : "برنامه را باز کن");\n        v.setProgressBar(R.id.w_bar, 100, fresh ? p.getInt("pct", 0) : 0, false);\n        v.setTextViewText(R.id.w_fin, p.getString("fin", ""));\n        String b = p.getString("img", "");\n        if (b.length() > 0) {\n            try {\n                byte[] d = Base64.decode(b, Base64.DEFAULT);\n                Bitmap bm = BitmapFactory.decodeByteArray(d, 0, d.length);\n                if (bm != null) v.setImageViewBitmap(R.id.w_img, bm);\n            } catch (Exception e) { }\n        }\n        Intent i = c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());\n        PendingIntent pi = PendingIntent.getActivity(c, 0, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);\n        v.setOnClickPendingIntent(R.id.w_root, pi);\n        return v;\n    }\n}\n', 'res/xml/sina_widget_info.xml': '<?xml version="1.0" encoding="utf-8"?>\n<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"\n    android:minWidth="110dp"\n    android:minHeight="110dp"\n    android:targetCellWidth="2"\n    android:targetCellHeight="2"\n    android:updatePeriodMillis="1800000"\n    android:initialLayout="@layout/widget_sina"\n    android:resizeMode="horizontal|vertical"\n    android:widgetCategory="home_screen"\n    android:description="@string/widget_desc" />\n', 'res/mipmap-anydpi-v26/ic_launcher_round.xml': '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n', 'res/mipmap-anydpi-v26/ic_launcher.xml': '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n', 'res/values/ic_launcher_background.xml': '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#000000</color>\n</resources>\n', 'res/values/sina_strings.xml': '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="widget_desc">پیشرفت تسک\u200cها و خرج هفتگی</string>\n</resources>\n', 'res/layout/widget_sina.xml': '<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n    android:id="@+id/w_root"\n    android:layout_width="match_parent"\n    android:layout_height="match_parent"\n    android:orientation="vertical"\n    android:padding="8dp"\n    android:layoutDirection="rtl"\n    android:background="@drawable/widget_bg">\n    <TextView\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:text="Planning"\n        android:textColor="#ECFAF3"\n        android:textStyle="bold"\n        android:textSize="11sp"\n        android:maxLines="1"\n        android:textDirection="ltr"\n        android:textAlignment="viewStart" />\n    <TextView\n        android:id="@+id/w_sum"\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:textColor="#A9CBC0"\n        android:textSize="10.5sp"\n        android:maxLines="1"\n        android:ellipsize="end"\n        android:textAlignment="viewStart" />\n    <ProgressBar\n        android:id="@+id/w_bar"\n        style="?android:attr/progressBarStyleHorizontal"\n        android:layout_width="match_parent"\n        android:layout_height="4dp"\n        android:layout_marginTop="4dp"\n        android:max="100"\n        android:progressTint="#3ECF9B"\n        android:progressBackgroundTint="#33FFFFFF" />\n    <ImageView\n        android:id="@+id/w_img"\n        android:layout_width="match_parent"\n        android:layout_height="34dp"\n        android:layout_marginTop="6dp"\n        android:scaleType="fitCenter" />\n    <TextView\n        android:id="@+id/w_fin"\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:textColor="#A9CBC0"\n        android:textSize="9.5sp"\n        android:maxLines="1"\n        android:ellipsize="end"\n        android:textAlignment="viewStart" />\n</LinearLayout>\n', 'res/drawable/widget_bg.xml': '<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <gradient android:startColor="#F20B1513" android:endColor="#F2101A2C" android:angle="315" />\n    <corners android:radius="24dp" />\n</shape>\n'}

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
    import base64
    KS = "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"
    with open(os.path.join(base, '..', '..', 'sina.keystore'), 'wb') as f:
        f.write(base64.b64decode(KS))
    gp = os.path.join(base, '..', '..', 'build.gradle')
    with open(gp, 'a', encoding='utf-8') as f:
        f.write("""
android {
    signingConfigs {
        debug {
            storeFile file('sina.keystore')
            storePassword 'android'
            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
    }
}
""")
    print('patched')

if __name__ == '__main__':
    {'prepare': prepare, 'patch': patch}[sys.argv[1]]()
