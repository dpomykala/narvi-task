from rest_framework import status
from rest_framework.test import APITestCase, RequestsClient

# TODO: Test also unhappy paths to ensure proper validation


class GroupingTasksApiTests(APITestCase):
    # Use integration type test to verify the entire workflow
    def test_grouping_tasks_workflow(self):
        client = RequestsClient()
        list_endpoint_url = "http://testserver/api/grouping-tasks/"

        # Create a new GroupingTask instance
        response = client.post(
            list_endpoint_url,
            json=dict(
                input_data=dict(
                    # Use custom delimiter
                    word_delimiter="-",
                    names=["foo", "foo-bar", "foo-baz", "xyz"],
                ),
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Response contain URL to the created resource
        response_data = response.json()
        self.assertIn("url", response_data)
        grouping_task_url = response_data["url"]

        # List all created GroupingTask instances
        response = client.get(list_endpoint_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["url"], grouping_task_url)

        # Retrieve the created GroupingTask instance
        response = client.get(grouping_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        # The grouping task instance contains correctly grouped names
        self.assertEqual(
            response_data["result"],
            dict(
                foo=["foo", "foo-bar", "foo-baz"],
                xyz=["xyz"],
            ),
        )

        # Move the xyz name to a different group
        grouping_task_move_url = f"{grouping_task_url}move-name/"
        response = client.patch(
            grouping_task_move_url,
            json=dict(
                name="xyz",
                source_group="xyz",
                target_group="foo",
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        # The name has been moved
        # The old group has been deleted
        # The new group has been created
        self.assertEqual(
            response_data["result"],
            dict(foo=["foo", "foo-bar", "foo-baz", "xyz"]),
        )
