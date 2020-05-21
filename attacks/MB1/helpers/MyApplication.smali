.class public X/MyApplication;
.super Landroid/app/Application;
.source "MyApplication.java"


# static fields
.field private static context:Landroid/content/Context;


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 6
    invoke-direct {p0}, Landroid/app/Application;-><init>()V

    return-void
.end method

.method public static getAppContext()Landroid/content/Context;
    .locals 1

    .line 15
    sget-object v0, X/MyApplication;->context:Landroid/content/Context;

    return-object v0
.end method


# virtual methods
.method public onCreate()V
    .locals 0

    .line 10
    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    .line 11
    invoke-virtual {p0}, X/MyApplication;->getApplicationContext()Landroid/content/Context;

    move-result-object p0

    sput-object p0, X/MyApplication;->context:Landroid/content/Context;

    return-void
.end method
