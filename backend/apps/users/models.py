from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    用户模型
    """
    # 手机号字段：字符串类型，最大长度20，允许为空，唯一约束
    phone = models.CharField("手机号", max_length=20, blank=True, null=True, unique=True)
    # 头像字段：URL类型，允许为空，默认值为空字符串
    avatar = models.URLField("头像", blank=True, default="")

    class Meta:
        # 后台管理界面显示的单数名称
        verbose_name = "用户"
        # 后台管理界面显示的复数名称
        verbose_name_plural = "用户"

    # 对象的字符串表示，后台列表页显示的内容，默认是username字段
    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    用户资料模型
    """
    # 一对一关联User模型：一个用户对应一份资料，一份资料属于一个用户，关联时级联删除用户资料，反向关联字段为profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    # 期望城市字段：字符串类型，最大长度100，允许为空，默认值为空字符串
    expected_city = models.CharField("期望城市", max_length=100, blank=True, default="")
    # 技能标签字段：文本类型，允许为空，默认值为空字符串
    skills = models.TextField("技能标签", blank=True, default="")
    # 简历文本字段：文本类型，允许为空，默认值为空字符串
    resume_text = models.TextField("简历文本", blank=True, default="")

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self):
        return f"{self.user.username} 的资料"


class Favorite(models.Model):
    """
    用户收藏岗位模型
    """
    # 外键关联User：一个用户可以有多个收藏
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites", verbose_name="用户")
    # 外键关联Job模型（来自jobs App）：一个岗位可以被多个用户收藏
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="favorited_by", verbose_name="岗位")
    # 收藏时间：创建时自动设置，之后不会改变
    created_at = models.DateTimeField("收藏时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = "用户收藏"
        # 联合唯一约束：同一个用户不能重复收藏同一个岗位
        unique_together = ("user", "job")

    def __str__(self):
        return f"{self.user.username} → {self.job.title}"


class BrowseHistory(models.Model):
    """
    用户浏览岗位历史模型
    """
    # 外键关联User：一个用户可以有多条浏览记录
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="browse_history", verbose_name="用户")
    # 外键关联Job模型（来自jobs App）：一个岗位可以被多个用户浏览
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="browse_history", verbose_name="岗位")
    # 浏览时间：创建时自动设置，之后不会改变
    browse_time = models.DateTimeField("浏览时间", auto_now_add=True)
    # 停留时长：整数类型，默认值为0
    stay_duration = models.IntegerField("停留时长(秒)", default=0)

    class Meta:
        verbose_name = "浏览历史"
        verbose_name_plural = "浏览历史"
        # 默认排序：按浏览时间倒序，最新的记录在最前面
        ordering = ["-browse_time"]

    def __str__(self):
        return f"{self.user.username} → {self.job.title} ({self.browse_time})"
