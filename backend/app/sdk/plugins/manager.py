import logging
import os
import json
import importlib.util
from typing import Dict, List, Type
from app.sdk.plugins.base import BasePlugin

logger = logging.getLogger("signalsense.plugins.manager")

class PluginManager:

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        
    def register_plugin(self, plugin: BasePlugin):

        if plugin.plugin_id in self._plugins:
            logger.warning(f"Plugin {plugin.plugin_id} is already registered. Overwriting.")
        self._plugins[plugin.plugin_id] = plugin
        logger.info(f"Registered plugin: {plugin.plugin_name} ({plugin.plugin_id})")
        
    def load_plugins_from_directory(self, plugins_dir: str):

        if not os.path.exists(plugins_dir):
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return
            
        for entry in os.scandir(plugins_dir):
            if entry.is_dir() and not entry.name.startswith("__"):
                manifest_path = os.path.join(entry.path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                            
                        # Extract metadata
                        plugin_id = manifest.get("plugin_id")
                        plugin_name = manifest.get("name")
                        
                        logger.info(f"Discovered plugin manifest: {plugin_name} ({plugin_id})")
                        
                        # Dynamically import plugin.py
                        plugin_module_path = os.path.join(entry.path, "plugin.py")
                        if os.path.exists(plugin_module_path):
                            spec = importlib.util.spec_from_file_location(f"signalsense.plugins.{plugin_id}", plugin_module_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Find the BasePlugin subclass
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                                    plugin_instance = attr(plugin_id=plugin_id, plugin_name=plugin_name)
                                    self.register_plugin(plugin_instance)
                                    break
                    except Exception as e:
                        logger.error(f"Failed to load plugin from {entry.path}: {e}")
        
    def get_plugin(self, plugin_id: str) -> BasePlugin:
        return self._plugins.get(plugin_id)
        
    def list_plugins(self) -> List[Dict[str, str]]:

        return [
            {"id": p.plugin_id, "name": p.plugin_name, "running": p._running}
            for p in self._plugins.values()
        ]
        
    async def start_all(self):

        logger.info(f"Starting {len(self._plugins)} plugins...")
        for plugin in self._plugins.values():
            if not plugin._running:
                await plugin.start()
                
    async def stop_all(self):

        logger.info("Stopping all plugins...")
        for plugin in self._plugins.values():
            if plugin._running:
                await plugin.stop()

# Global Singleton
plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    return plugin_manager
