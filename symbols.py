
import layers
import library
import logging
import os


_log = logging.getLogger("lvl")


class SymbolTable:
    def __init__(self):
        self._symbols = {}
        for layer in layers.LAYERS_ORDERING:
            self._loadSymbolsForLayer(layer)

        self._definitionsPerLibrary = self._constructDefinitionsPerLibrary()
        self._referencesPerLibrary = self._constructReferencesPerLibrary()

        layers.LAYERS["Ignored"]["libraries"].append("dummylib")
        self._symbols["_GLOBAL_OFFSET_TABLE_"] = { "definitions": ["dummylib"], "references": [] }
        self._symbols["__gmon_start__"] = { "definitions": ["dummylib"], "references": [] }
        self._symbols["_Jv_RegisterClasses"] = { "definitions": ["dummylib"], "references": [] }
        self._definitionsPerLibrary["dummylib"] = ["_GLOBAL_OFFSET_TABLE_", "__gmon_start__", "_Jv_RegisterClasses"]
        self._referencesPerLibrary["dummylib"] = []

    def _loadSymbolsForLayer(self, layer):
        _log.info("Loading symbols for layer '%s' ..." % layer)
        for layerLibrary in layers.LAYERS[layer]["libraries"]:
            self._loadSymbolsFromLibrary(library.Library(layerLibrary), layer)
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
        for layer in layers.LAYERS_ORDERING:
            for library in layers.LAYERS[layer]["libraries"]:
                assert library not in definitionsPerLibrary
                definitionsPerLibrary[library] = []

        for symbol in self._symbols:
            for library in self._symbols[symbol]["definitions"]:
                assert library in definitionsPerLibrary
                definitionsPerLibrary[library].append(symbol)

        return definitionsPerLibrary

    def _constructReferencesPerLibrary(self):
        referencesPerLibrary = {}
        for layer in layers.LAYERS_ORDERING:
            for library in layers.LAYERS[layer]["libraries"]:
                assert library not in referencesPerLibrary
                referencesPerLibrary[library] = []

        for symbol in self._symbols:
            for library in self._symbols[symbol]["references"]:
                assert library in referencesPerLibrary
                referencesPerLibrary[library].append(symbol)

        return referencesPerLibrary

    def symbolsReferencedInLayer(self, layer):
        referencedSymbols = []
        for library in layers.LAYERS[layer]["libraries"]:
            referencedSymbols.extend(self._referencesPerLibrary[library])
        return referencedSymbols

    def symbolDefinedBeforeReferenced(self, symbol, referringLayer):

        def symbolDefinedInLayer(layer):
            assert layer in layers.LAYERS
            symbolDefined = any(map(lambda x: symbol in self._definitionsPerLibrary[x], layers.LAYERS[layer]["libraries"]))
            return symbolDefined or any(map(lambda x: symbolDefinedInLayer(x), layers.LAYERS[layer]["dependencies"]))

        return symbolDefinedInLayer(referringLayer)

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
