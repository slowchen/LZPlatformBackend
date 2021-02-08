from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from ..core.response import APIResponse
from utils.utils import now


class APIModelViewSet(ModelViewSet):
    """
    自定义ViewSet，主要实现在写数据到model时保存当前操作用户，及返回response时使用自定义的APIResponse类
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': self.request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
        return APIResponse(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': self.request})
        return APIResponse(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            model = serializer.Meta.model
            if hasattr(model, 'create_by'):
                serializer.save(create_by=request.user)
            if hasattr(model, 'update_by'):
                serializer.save(update_by=request.user)
            if not hasattr(model, 'create_by') and not hasattr(model, 'update_by'):
                serializer.save()
            headers = self.get_success_headers(serializer.data)
            return APIResponse(serializer.data, msg='创建成功', headers=headers)
        raise ValidationError(serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial,
                                         context={'request': self.request})
        if serializer.is_valid():
            model = serializer.Meta.model
            if hasattr(model, 'update_by'):
                serializer.save(update_by=request.user)
            else:
                serializer.save()
            return APIResponse(serializer.data, msg='更新成功')
        raise ValidationError(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if hasattr(instance, 'update_by'):
            instance.update_by = request.user
        if hasattr(instance, 'update_time'):
            instance.update_time = now()
        instance.save()
        return APIResponse(msg='删除成功')
