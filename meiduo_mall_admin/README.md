# meiduo_mall

> A Vue.js project

##### 1、安装依赖

```shell
# install dependencies
npm install
```

##### 2、编译出静态文件(编译好的静态文件存储在dist目录)

```shell
# build for production with minification
npm run build
```

##### 3、运行开发服务器

###### 3.1、第一种方式(端口号固定8081)

``` bash
cd meiduo_mall_admin
# serve with hot reload at localhost:8080
npm run dev
```

###### 3.2、第二种运行方式

```shell
cd meiduo_mall_admin/dist
python3 -m http.server <端口号>
```

