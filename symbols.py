
import library
import logging
import os


_log = logging.getLogger("lvl")


LAYERS = [
    {
        "name": "Ignored", # FIXME: Let's not, if possible.
        "libraries": [],
        "symbols": {
            "_GLOBAL_OFFSET_TABLE_": { "definitions": ["ignore"], "references": [] },
        },
        "skipAnalysis": True,
    },
    {
        "name": "SystemDeps",
        "libraries": [
            { "name": "atk", "fileName": "libatk-1.0.so", "shared": True },
            { "name": "cairo", "fileName": "libcairo.so", "shared": True },
            { "name": "EGL", "fileName": "libEGL.so", "shared": True },
            { "name": "enchant", "fileName": "libenchant.so", "shared": True },
            { "name": "fontconfig", "fileName": "libfontconfig.so", "shared": True },
            { "name": "freetype", "fileName": "libfreetype.so", "shared": True },
            { "name": "GL", "fileName": "libGL.so", "shared": True },
            { "name": "gailutil", "fileName": "libgailutil-3.so", "shared": True },
            { "name": "gdkpixbuf", "fileName": "libgdk_pixbuf-2.0.so", "shared": True },
            { "name": "gdk", "fileName": "libgdk-3.so", "shared": True },
            { "name": "geoclue", "fileName": "libgeoclue.so", "shared": True },
            { "name": "gio", "fileName": "libgio-2.0.so", "shared": True },
            { "name": "glib", "fileName": "libglib-2.0.so", "shared": True },
            { "name": "gmodule", "fileName": "libgmodule-2.0.so", "shared": True },
            { "name": "gobject", "fileName": "libgobject-2.0.so", "shared": True },
            { "name": "gstapp", "fileName": "libgstapp-1.0.so", "shared": True },
            { "name": "gstaudio", "fileName": "libgstaudio-1.0.so", "shared": True },
            { "name": "gstbase", "fileName": "libgstbase-1.0.so", "shared": True },
            { "name": "gstfft", "fileName": "libgstfft-1.0.so", "shared": True },
            { "name": "gstpbutils", "fileName": "libgstpbutils-1.0.so", "shared": True },
            { "name": "gstreamer", "fileName": "libgstreamer-1.0.so", "shared": True },
            { "name": "gstvideo", "fileName": "libgstvideo-1.0.so", "shared": True },
            { "name": "gthread", "fileName": "libgthread-2.0.so", "shared": True },
            { "name": "gtk", "fileName": "libgtk-3.so", "shared": True },
            { "name": "gudev", "fileName": "libgudev-1.0.so", "shared": True },
            { "name": "harfbuzz", "fileName": "libharfbuzz.so", "shared": True },
            { "name": "icudata", "fileName": "libicudata.so", "shared": True },
            { "name": "icui18n", "fileName": "libicui18n.so", "shared": True },
            { "name": "icuuc", "fileName": "libicuuc.so", "shared": True },
            { "name": "jpeg", "fileName": "libjpeg.so", "shared": True },
            { "name": "libc", "fileName": "libc.a" },
            { "name": "libgcc", "fileName": "libgcc_s.so.1", "shared": True },
            { "name": "libm", "fileName": "libm.a" },
            { "name": "libsecret", "fileName": "libsecret-1.so", "shared": True },
            { "name": "libsoup", "fileName": "libsoup-2.4.so", "shared": True },
            { "name": "pango", "fileName": "libpango-1.0.so", "shared": True },
            { "name": "pangocairo", "fileName": "libpangocairo-1.0.so", "shared": True },
            { "name": "png", "fileName": "libpng.so", "shared": True },
            { "name": "pthread", "fileName": "libpthread.a" },
            { "name": "sqlite3", "fileName": "libsqlite3.so", "shared": True },
            { "name": "stdc++", "fileName": "libstdc++.so.6", "shared": True },
            { "name": "X11", "fileName": "libX11.so", "shared": True },
            { "name": "Xcomposite", "fileName": "libXcomposite.so", "shared": True },
            { "name": "Xdamage", "fileName": "libXdamage.so", "shared": True },
            { "name": "Xfixes", "fileName": "libXfixes.so", "shared": True },
            { "name": "Xrender", "fileName": "libXrender.so", "shared": True },
            { "name": "Xt", "fileName": "libXt.so", "shared": True },
            { "name": "webp", "fileName": "libwebp.so", "shared": True },
            { "name": "zlib", "fileName": "libz.so", "shared": True },

            # FIXME: uncomment when required
            # { "name": "libxml2", "fileName": "libxml2.so", "shared": True },
        ],
        "symbols": {},
        "skipAnalysis": True,
    },
    {
        "name": "InTreeDeps",
        "libraries": [
            { "name": "LevelDB", "fileName": "libLevelDB.a" },
            { "name": "ANGLE", "fileName": "libANGLE.a" },
        ],
        "symbols": {},
    },
    {
        "name": "WTF",
        "libraries": [
            { "name": "WTF", "fileName": "libWTF.a" },
        ],
        "symbols": {},
    },
    {
        "name": "Platform",
        "libraries": [
            { "name": "Platform", "fileName": "libPlatform.a" },
            { "name": "PlatformGTK", "fileName": "libPlatformGtk.a" },
            { "name": "WebCorePlatform", "fileName": "libWebCorePlatform.a" },
            { "name": "WebCoreGTK", "fileName": "libWebCoreGtk.a" },
        ],
        "symbols": {},
        "storeObjectFileAsLocation": True,
    },
];


class SymbolTable:
    def __init__(self):
        self._symbols = {}
        for layer in LAYERS:
            self._loadSymbolsForLayer(layer)

        self._definitionsPerLibrary = self._constructDefinitionsPerLibrary()
        self._referencesPerLibrary = self._constructReferencesPerLibrary()

        LAYERS[0]["libraries"] = [{ "name": "Dummy library", "fileName": "dummylib" }]
        self._symbols["_GLOBAL_OFFSET_TABLE_"] = { "definitions": ["dummylib"], "references": [] }
        self._definitionsPerLibrary["dummylib"] = ["_GLOBAL_OFFSET_TABLE_"]
        self._referencesPerLibrary["dummylib"] = []

    def _loadSymbolsForLayer(self, layer):
        _log.info("Loading symbols for layer '%s' ..." % layer["name"])
        for libraryObject in layer["libraries"]:
            self._loadSymbolsFromLibrary(library.Library(libraryObject["fileName"]), layer)
        _log.info("... Done.")

    def _loadSymbolsFromLibrary(self, libraryLoader, layer):
        _log.debug("    Loading symbols from library '%s' ..." % libraryLoader.libraryName)
        self._storeSymbolsForLayer(libraryLoader.definedSymbols(), True, libraryLoader, layer)
        self._storeSymbolsForLayer(libraryLoader.referencedSymbols(), False, libraryLoader, layer)

    def _storeSymbolsForLayer(self, symbolsObject, defined, libraryLoader, layer):
        assert (symbolsObject.keys() != ["so"]) is not libraryLoader.isSharedLibrary
        for originatingObject, symbolsList in symbolsObject.items():
            for symbol in symbolsList:
                if symbol not in self._symbols:
                    self._symbols[symbol] = { "definitions": [], "references": [] }
                self._symbols[symbol]["definitions" if defined else "references"].append(libraryLoader.libraryName)
                if originatingObject == "so" or defined:
                    continue
                if "objectFiles" not in self._symbols[symbol]:
                    self._symbols[symbol]["objectFiles"] = []
                self._symbols[symbol]["objectFiles"].append(originatingObject)

    def _constructDefinitionsPerLibrary(self):
        definitionsPerLibrary = {}
        for layer in LAYERS:
            for library in layer["libraries"]:
                assert library["fileName"] not in definitionsPerLibrary
                definitionsPerLibrary[library["fileName"]] = []

        for symbol in self._symbols:
            for library in self._symbols[symbol]["definitions"]:
                assert library in definitionsPerLibrary
                definitionsPerLibrary[library].append(symbol)

        return definitionsPerLibrary

    def _constructReferencesPerLibrary(self):
        referencesPerLibrary = {}
        for layer in LAYERS:
            for library in layer["libraries"]:
                assert library["fileName"] not in referencesPerLibrary
                referencesPerLibrary[library["fileName"]] = []

        for symbol in self._symbols:
            for library in self._symbols[symbol]["references"]:
                assert library in referencesPerLibrary
                referencesPerLibrary[library].append(symbol)

        return referencesPerLibrary

    def symbolsReferencedInLayer(self, layer):
        layerLibraryNames = map(lambda x: x["fileName"], layer["libraries"])
        referencedSymbols = []
        for library in layerLibraryNames:
            referencedSymbols.extend(self._referencesPerLibrary[library])
        return referencedSymbols

    def symbolDefinedBeforeReferenced(self, symbol, referringLayer):
        assert referringLayer in LAYERS
        referringLayerPos = LAYERS.index(referringLayer)
        targetLayers = LAYERS[:referringLayerPos + 1]

        for layer in targetLayers:
            for library in layer["libraries"]:
                assert library["fileName"] in self._definitionsPerLibrary
                if symbol in self._definitionsPerLibrary[library["fileName"]]:
                    return True
        return False

    def librariesDefiningSymbol(self, symbol):
        assert symbol in self._symbols
        return self._symbols[symbol]["definitions"] or ["No known libraries define `%s`" % symbol]

    def librariesReferencingSymbol(self, symbol):
        assert symbol in self._symbols
        return self._symbols[symbol]["references"] or ["No known libraries reference `%s`" % symbol]

    def objectFilesReferencingSymbol(self, symbol):
        assert symbol in self._symbols
        if "objectFiles" in self._symbols[symbol]:
            return map(lambda x: os.path.relpath(x) if os.path.isabs(x) else x, self._symbols[symbol]["objectFiles"])
        return ["None/Unknown"]
