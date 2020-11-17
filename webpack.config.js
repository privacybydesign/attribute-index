const path = require('path');

module.exports = {
  target: 'web',
  entry: './src/index.js',
  output: {
    filename: 'script.js',
    libraryTarget: 'umd',
    path: path.resolve(__dirname)
  }
};
