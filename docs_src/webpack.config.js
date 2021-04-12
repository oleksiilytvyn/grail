/***
 * Bundle frontend files
 */
const fs = require('fs');
const path = require('path');
const CopyPlugin = require("copy-webpack-plugin");
const TerserPlugin = require('terser-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');
const { extendDefaultPlugins } = require('svgo');

module.exports = {
    mode: 'production', // production, development
    devtool: false,
    // target: 'web',
    entry: {
        index: path.resolve(__dirname, './js/page.js')
    },
    output: {
        clean: true,
        filename: '[name].js',
        path: path.resolve(__dirname, '../docs')
    },
    resolve: {
        modules: ['node_modules'],
    },
    optimization: {
        minimize: true,
        runtimeChunk: 'single'
    },
    module: {
        rules: [
        {
            test: /\.(png|svg|jpg|jpeg|gif)$/i,
            exclude: /node_modules/,
            use: [{
                loader: 'url-loader',
                options: {
                    limit: 4000, // inline images up to 4k bytes
                    name: '[name].[ext]',
                    outputPath: './assets',
                    publicPath: '../assets'
                }
            }]
        },
        {
            test: /\.html&/,
            exclude: /node_modules/,
            use: ['html-loader']
        },
        {
            test: /\.ts$/,
            exclude: /node_modules/,
            use: "ts-loader"
        },
        {
            test: /\.(js)$/,
            exclude: /node_modules/,
            use: "babel-loader"
        },
        {
            test: /\.scss$/,
            exclude: /node_modules/,
            use: [
                MiniCssExtractPlugin.loader,
                'css-loader',
                // 'postcss-loader',
                'sass-loader'
            ]
        }]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: "css/[name].css",
            chunkFilename: "[id].css"
        }),
        new ImageMinimizerPlugin({
            test: /\.(jpe?g|png|gif|svg)$/i,
            minimizerOptions: {
                plugins: [
                    ['gifsicle', { interlaced: true }],
                    ['jpegtran', { progressive: true }],
                    ['optipng', { optimizationLevel: 5 }],
                    [
                        'svgo',
                        {
                            plugins: extendDefaultPlugins([
                                {
                                    name: 'removeViewBox',
                                    active: false,
                                },
                            ]),
                        },
                    ],
                ],
            },
        }),
        new CopyPlugin({
            patterns: [
                // Copy static assets
                {
                    from: "./assets",
                    to:   "./assets",
                    globOptions: { ignore: ['*.DS_Store', 'Thumbs.db'] }
                },
                {
                    from: "./static",
                    to:   "./"
                }
            ],
        }),
        new HtmlWebpackPlugin({
            template: "./templates/index.html",
            inject: true,
            chunks: ['index'],
            filename: 'index.html',
        }),
        new HtmlWebpackPlugin({
            template: "./templates/bibles.html",
            inject: true,
            chunks: ['index'],
            filename: 'bibles.html'
        }),
    ],
    devServer: {
        contentBase: path.join(__dirname, '../docs'),
        compress: true,
        port: 9000,
        hot: true,
        writeToDisk: true,
    },
};