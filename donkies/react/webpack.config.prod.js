var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');

var HTMLWebpackPluginConfig = new HtmlWebpackPlugin({
    template: __dirname + '/src/index.html',
    hash: true,
    filename: 'index.html',
    inject: 'body'
});

module.exports = {
    devtool: 'source-map',
    
    entry: [
        './src/index.js'
    ],
    
    output: {
        path: 'dist',
        filename: 'index_bundle.js',
        publicPath: '/'
    },
    
    module: {
        loaders: [
            {
                test: /\.js$/,
                loaders: ['babel'],
                include: __dirname + '/src'
            },
            {
                test: /\.css$/,
                loader: 'style-loader!css-loader',
                include: __dirname + '/src'
            },
        ]
    },
    
    resolve: {
        root: [path.resolve('./src'), path.resolve('./node_modules')],
        extensions: ['', '.js']
    },
    
    plugins: [HTMLWebpackPluginConfig],
    
    devServer: {
        contentBase: __dirname + '/dist',
        historyApiFallback: true
    }
};
