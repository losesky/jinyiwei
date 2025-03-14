module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // 查找 ForkTsCheckerWebpackPlugin 插件
      const tsCheckerPlugin = webpackConfig.plugins.find(
        (plugin) => plugin.constructor.name === 'ForkTsCheckerWebpackPlugin'
      );
      
      // 如果找到了插件，增加内存限制
      if (tsCheckerPlugin) {
        tsCheckerPlugin.options.memoryLimit = 4096; // 增加到 4GB
      }
      
      return webpackConfig;
    },
  },
  // 减少并行处理的数量，降低内存使用
  jest: {
    configure: {
      maxWorkers: '50%',
    },
  },
}; 