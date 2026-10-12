set -e
APP=android/app/src/main
mkdir -p $APP/java/com/sina/planner
cp android-overlay/java/*.java $APP/java/com/sina/planner/
cp -r android-overlay/res/. $APP/res/
python3 - <<'PY'
p='android/app/src/main/AndroidManifest.xml'
s=open(p,encoding='utf-8').read()
r='''<receiver android:name=".SinaWidget" android:exported="true">
  <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
  <meta-data android:name="android.appwidget.provider" android:resource="@xml/sina_widget_info"/>
</receiver>
'''
s=s.replace('</application>',r+'</application>',1)
s=s.replace('</manifest>','<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>\n<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>\n</manifest>',1)
open(p,'w',encoding='utf-8').write(s)
PY
echo patched
