from rest_framework import serializers

from words.word_trie import WordTrie
from .models import GroupingTask


class GroupingTaskIdentitySerializer(serializers.HyperlinkedModelSerializer):
    """The representation of a grouping task resource identity using a hyperlink."""

    url = serializers.HyperlinkedIdentityField(view_name="grouping-task-detail")

    class Meta:
        model = GroupingTask
        fields = ("url",)


class GroupingTaskSerializer(GroupingTaskIdentitySerializer):
    """The representation of a grouping task resource."""

    class Meta:
        model = GroupingTask
        exclude = ("input_data",)


class GroupingTaskInputDataSerializer(serializers.Serializer):
    """The representation of input data required for grouping names."""

    word_delimiter = serializers.CharField(
        max_length=1, required=False, default=WordTrie.DEFAULT_WORD_DELIMITER
    )
    names = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class GroupingTaskCreateSerializer(serializers.ModelSerializer):
    """The representation of data required to create a grouping task."""

    input_data = GroupingTaskInputDataSerializer()

    class Meta:
        model = GroupingTask
        fields = ("input_data",)

    def to_representation(self, instance):
        # Provide the URL to the created resource in the response
        return GroupingTaskIdentitySerializer(context=self.context).to_representation(
            instance
        )


class GroupingTaskMoveNameSerializer(serializers.Serializer):
    """The representation of data required to move a name between groups."""

    name = serializers.CharField()
    source_group = serializers.CharField()
    target_group = serializers.CharField()
