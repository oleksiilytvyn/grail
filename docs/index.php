<?php

/**
 * A really little piece of routing engine
 */

if (isset($_GET['url']) && $_GET['url'] == 'ru'){
	// Russian
	require './ru.html';
} else if (isset($_GET['url']) && $_GET['url'] == 'en'){
	// English
	require './en.html';
} else if (isset($_GET['url']) && $_GET['url'] == 'bibles'){
	// English
	require './bibles.html';
} else if (isset($_GET['url']) && !empty($_GET['url'])){
	// Redirect to main page in any other situation
	header("Location: http://" . $_SERVER['SERVER_NAME'] . "/");
	die();
} else {
	// Default web page
	require './en.html';
}
