LAYERS = {
    "Ignored": {
        "skipAnalysis": True,
        "libraries": [],
        "dependencies": [],
    },

    "SystemDeps": {
        "skipAnalysis": True,
        "libraries": [
            "libatk-1.0.so", "libcairo.so", "libdl.so", "libEGL.so", "libenchant.so", "libfontconfig.so", "libfreetype.so",
            "libGL.so", "libgailutil-3.so", "libgdk_pixbuf-2.0.so", "libgdk-3.so", "libgeoclue.so", "libgio-2.0.so",
            "libglib-2.0.so", "libgmodule-2.0.so", "libgobject-2.0.so", "libgstapp-1.0.so", "libgstaudio-1.0.so",
            "libgstbase-1.0.so", "libgstfft-1.0.so", "libgstpbutils-1.0.so", "libgstreamer-1.0.so",
            "libgstvideo-1.0.so", "libgthread-2.0.so", "libgtk-3.so", "libgudev-1.0.so", "libharfbuzz.so",
            "libicudata.so", "libicui18n.so", "libicuuc.so", "libitm.so.1", "libjpeg.so", "libc.a", "libgcc_s.so.1",
            "libm.a", "libsecret-1.so", "libsoup-2.4.so", "libpango-1.0.so", "libpangocairo-1.0.so", "libpng.so",
            "libpthread.a", "libsqlite3.so", "libstdc++.so.6", "libupower-glib.so", "libwebp.so", "libX11.so",
            "libXcomposite.so", "libXdamage.so", "libXfixes.so", "libXrender.so", "libXt.so", "libxml2.so", "libxslt.so", "libz.so",
        ],
        "dependencies": [],
    },

    "InTreeDeps": {
        "libraries": ["libLevelDB.a", "libANGLE.a"],
        "dependencies": ["SystemDeps", "Ignored"],
    },

    "WTF": {
        "libraries": ["libWTF.a"],
        "dependencies": ["SystemDeps", "Ignored"],
    },

    "JavaScriptCore": {
        "libraries": ["libjavascriptcoregtk-3.0.so"],
        "dependencies": ["SystemDeps", "Ignored"],
    },

    "Platform": {
        "libraries": ["libPlatform.a", "libPlatformGtk.a"],
        "dependencies": ["JavaScriptCore", "WTF", "InTreeDeps"],
    },

    "WebCorePlatform": {
        "libraries": ["libWebCorePlatform.a", "libWebCoreGtk.a"],
        "dependencies": ["WTF", "InTreeDeps"]
    },

    "WebCore": {
        "skipAnalysis": True,
        "libraries": ["libWebCore.a", "libWebCoreModules.a", "libWebCoreSVG.a"],
        "dependencies": ["JavaScriptCore", "Platform", "WebCorePlatform"],
    },
}

LAYERS_ORDERING = [
    "Ignored",
    "SystemDeps",
    "InTreeDeps",
    "WTF",
    "JavaScriptCore",
    "Platform",
    "WebCorePlatform",
    "WebCore",
]
