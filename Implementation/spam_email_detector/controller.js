app.controller("SpamController", function($scope, $http) {
    $scope.result = "";
  
    $scope.checkSpam = function() {
      $http.post("http://localhost:5000/api/check_spam", {
        text: $scope.emailContent
      }).then(function(response) {
        $scope.result = response.data.is_spam ? "Spam!" : "Not Spam!";
      }, function(error) {
        $scope.result = "Error connecting to server.";
      });
    };
  });
  