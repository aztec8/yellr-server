'use strict';

angular
    .module('Yellr')
    .controller('viewPostModalCtrl',
    ['$scope', '$rootScope', '$modalInstance', 'assignmentApiService',
    function ($scope, $rootScope, $modalInstance, assignmentApiService) {

        assignmentApiService.registerPostViewed($scope.postId);

        assignmentApiService.getPost($scope.postId)
        .success(function (data) {
            $scope.post = data.post;
        });

    }]);
