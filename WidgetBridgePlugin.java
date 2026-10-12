package com.sina.planner;

import android.content.Context;
import android.content.SharedPreferences;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "WidgetBridge")
public class WidgetBridgePlugin extends Plugin {
    @PluginMethod
    public void update(PluginCall call) {
        SharedPreferences.Editor e = getContext().getSharedPreferences("sina_widget", Context.MODE_PRIVATE).edit();
        e.putString("day", call.getString("day", ""));
        e.putString("summary", call.getString("summary", ""));
        e.putString("lines", call.getString("lines", ""));
        e.putInt("pct", call.getInt("pct", 0));
        e.apply();
        SinaWidget.refreshAll(getContext());
        call.resolve();
    }
}
