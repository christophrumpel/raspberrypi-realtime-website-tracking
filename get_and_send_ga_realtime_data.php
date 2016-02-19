<?php

// Source: https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime/get

require_once('pubnub-lib/autoloader.php');

use Pubnub\Pubnub;

$pubnub = new Pubnub(array(
    'subscribe_key' => 'insert-your-pubnub-subscribe-key',
    'publish_key'   => 'insert-your-pubnub-publish-key'
));

function getService()
{
  // Creates and returns the Analytics service object.

  // Load the Google API PHP Client Library.
  require_once 'google-api-php-client/src/Google/autoload.php';

  // Use the developers console and replace the values with your
  // service account email, and relative location of your key file.
  $service_account_email = 'your-service-account-email';
  $key_file_location = 'your-client-secret-file';

  // Create and configure a new client object.
  $client = new Google_Client();
  $client->setApplicationName("HelloAnalytics");
  $analytics = new Google_Service_Analytics($client);

  // Read the generated client_secrets.p12 key.
  $key = file_get_contents($key_file_location);
  $cred = new Google_Auth_AssertionCredentials(
      $service_account_email,
      array(Google_Service_Analytics::ANALYTICS_READONLY),
      $key
  );
  $client->setAssertionCredentials($cred);
  if($client->getAuth()->isAccessTokenExpired()) {
    $client->getAuth()->refreshTokenWithAssertion($cred);
  }

  return $analytics;
}

$analytics = getService();

/**
 * 1.Create and Execute a Real Time Report
 * An application can request real-time data by calling the get method on the Analytics service object.
 * The method requires an ids parameter which specifies from which view (profile) to retrieve data.
 */
$optParams = array(
    'dimensions' => 'rt:medium,rt:city,rt:country'
);

try {

  // How to find your GA profile view id:
  // Go to GA. Get to your site.
  // When you're on the dashboard you will see the ID in your URL at the end.
  // It's the number after the "p".
  $results = $analytics->data_realtime->get(
      'ga:INSERT-YOUR-GA-PROFILE-VIEW-ID',
      'rt:activeUsers',
      $optParams);

  // print_r($results);
  $activeUserCount = $results->totalsForAllResults['rt:activeUsers'];
  $country = $results->getRows()[0][2];
  $city = $results->getRows()[0][1];

  if($activeUserCount > 0) {
    $info = $pubnub->publish('analytics-channel', ['led' => 1, 'city' => $city, 'country' => $country]);
  } else {
    $info = $pubnub->publish('analytics-channel', ['led' => 0]);
  }

  var_dump($info);



  // Success. 
} catch (apiServiceException $e) {
  // Handle API service exceptions.
  $error = $e->getMessage();
}




?>
