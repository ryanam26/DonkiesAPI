var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');


module.exports = {
    devtool: 'cheap-module-source-map',

    entry: [
        'react-hot-loader/patch',
        'webpack-dev-server/client?http://localhost:8080',
        'webpack/hot/only-dev-server',
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
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader!resolve-url!sass-loader?sourceMap')
            },
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
            },
            {
                test: /\.woff2?$|\.ttf$|\.eot$|\.svg$|\.png|\.jpe?g|\.gif$/,
                loader: 'file-loader'
            }
        ]
    },

    resolve: {
        root: [path.resolve('./src'), path.resolve('./node_modules')],
        extensions: ['', '.js', '.css', 'scss']
    },

    plugins: [
        new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new ExtractTextPlugin('css/style_bundle.css', {
            allChunks: true
        })
    ],

    devServer: {
        contentBase: __dirname + '/dist',
        historyApiFallback: true,
        // hot: true
    },
}